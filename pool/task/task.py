from faker import Faker
import random
from database.mongodb import (
    AiTask,
    ResponseTask,
    ValidationTask,
    ValidationTaskHistory,
    userStats,
    fs,
)
from utils.layout import base
from datetime import datetime, timedelta
import uuid_utils as uuid
import json
from pymongo.errors import PyMongoError
from bson.binary import Binary
import math
import logging

from task.prompt import generate_random_image_prompt


faker = Faker()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


async def generate_task():
    # This function was created as a simulation of generate_task user-given task from the database. You can modify it to suit your specific requirements.
    try:
        # Generate random text for the task
        prompt = generate_random_image_prompt()
        negative_prompt = base["PROMPT"]["NEGATIVE"]
        width = base["PROMPT"]["WIDTH"]
        height = base["PROMPT"]["HEIGHT"]
        current_time = datetime.utcnow().isoformat()
        wallet_address = ""
        status = "pending"
        unique_id = str(uuid.uuid4())
        retrieve_id = str(uuid.uuid7())
        seed = random.randint(1, 9223372036854775807)
        seed_str = f"{seed}"
        message_type = "requestedTask"

        # Create the task document
        task_document = {
            "id": unique_id,
            "task": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "seed": seed_str,
            "time": current_time,
            "retrieve_id": retrieve_id,
            "wallet": wallet_address,
            "status": status,
            "type": "medium",
            "message_type": message_type,
        }

        # Insert the task document into the AiTask collection
        insert_result = AiTask.insert_one(task_document)
        # Check if the insertion was acknowledged by MongoDB
        if insert_result.acknowledged:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"An error occurred in generate_task: {e}")
        return False


async def generate_automatic_task(walletAddress):
    try:
        prompt = generate_random_image_prompt()
        negative_prompt = base["PROMPT"]["NEGATIVE"]
        width = base["PROMPT"]["WIDTH"]
        height = base["PROMPT"]["HEIGHT"]
        current_time = datetime.utcnow().isoformat()
        wallet_address = walletAddress
        status = "sent"
        type = "low"
        unique_id = str(uuid.uuid4())
        retrieve_id = str(uuid.uuid7())
        seed = random.randint(1, 9223372036854775807)
        seed_str = f"{seed}"
        message_type = "requestedTask"

        task_document = {
            "id": unique_id,
            "negative_prompt": negative_prompt,
            "task": prompt,
            "width": width,
            "height": height,
            "seed": seed_str,
            "time": current_time,
            "retrieve_id": retrieve_id,
            "wallet": wallet_address,
            "status": status,
            "type": type,
            "message_type": message_type,
        }

        insert_result = AiTask.insert_one(task_document)
        if insert_result.acknowledged:
            return {
                "id": unique_id,
                "task": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "seed": seed_str,
                "message_type": message_type,
            }
        else:
            return None
    except Exception as e:
        logging.error(f"An error occurred in generate_automatic_task: {e}")
        return None


async def update_task(document_id, wallet_address):
    current_time = datetime.utcnow().isoformat()
    update_result = AiTask.update_one(
        {"id": document_id},
        {"$set": {"wallet": wallet_address, "time": current_time, "status": "sent"}},
    )
    return update_result.acknowledged


async def find_task(wallet_address):
    try:
        two_minutes_ago = datetime.utcnow() - timedelta(minutes=2)

        # First, check if the wallet_address has any 'sent' task that is not completed
        pending_task = AiTask.find_one({"wallet": wallet_address, "status": "sent"})

        if pending_task:

            return pending_task["id"], json.dumps(
                {
                    "id": pending_task["id"],
                    "task": pending_task["task"],
                    "negative_prompt": pending_task["negative_prompt"],
                    "width": pending_task["width"],
                    "height": pending_task["height"],
                    "seed": pending_task.get("seed"),
                    "message_type": pending_task.get("message_type"),
                }
            )

        # Define a priority dictionary
        priority_map = {"high": 1, "medium": 2, "low": 3}

        # Find tasks sorted by time
        tasks = AiTask.find().sort("time", 1)

        # Convert cursor to a list
        tasks_list = list(tasks)

        # If no tasks found in db, generate a new automatic task
        if not tasks_list:

            new_task = await generate_automatic_task(wallet_address)
            if new_task:
                return new_task["id"], json.dumps(
                    {
                        "id": new_task["id"],
                        "task": new_task["task"],
                        "negative_prompt": new_task["negative_prompt"],
                        "width": new_task["width"],
                        "height": new_task["height"],
                        "seed": new_task.get("seed"),
                        "message_type": new_task.get("message_type"),
                    }
                )
            else:
                return None, None

        # Sort tasks by priority if there are tasks
        tasks_list.sort(key=lambda task: priority_map.get(task.get("type", "low"), 3))

        for task in tasks_list:
            if (
                task["status"] == "sent"
                and datetime.fromisoformat(task["time"]) < two_minutes_ago
            ):
                if await update_task(task["id"], wallet_address):
                    return task["id"], json.dumps(
                        {
                            "id": task["id"],
                            "task": task["task"],
                            "negative_prompt": task["negative_prompt"],
                            "width": task["width"],
                            "height": task["height"],
                            "seed": task.get("seed"),
                            "message_type": task.get("message_type"),
                        }
                    )
            elif task["status"] == "pending":
                if await update_task(task["id"], wallet_address):
                    return task["id"], json.dumps(
                        {
                            "id": task["id"],
                            "task": task["task"],
                            "negative_prompt": task["negative_prompt"],
                            "width": task["width"],
                            "height": task["height"],
                            "seed": task.get("seed"),
                            "message_type": task.get("message_type"),
                        }
                    )

        # If no suitable task is found, generate a new automatic task
        new_task = await generate_automatic_task(wallet_address)
        if new_task:
            return new_task["id"], json.dumps(
                {
                    "id": new_task["id"],
                    "task": new_task["task"],
                    "negative_prompt": new_task["negative_prompt"],
                    "width": new_task["width"],
                    "height": new_task["height"],
                    "seed": new_task.get("seed"),
                    "message_type": new_task.get("message_type"),
                }
            )
        else:
            return None, None
    except Exception as e:
        logging.error(f"An error occurred in find_task: {e}")
        return None, None


async def store_response(task_id, wallet_address, output, retrieve_id):
    try:
        # Calculate the expiration time
        expire_at = datetime.utcnow() + timedelta(minutes=3)

        # Create the response document
        response_document = {
            "retrieve_id": retrieve_id,
            "wallet_address": wallet_address,
            "output": Binary(output),
            "task_id": task_id,
            "expireAt": expire_at,
        }

        # Insert the response document into the ResponseTask collection
        insert_result = ResponseTask.insert_one(response_document)

        if insert_result.acknowledged:
            return True, "Response stored successfully"
        else:
            return False, "Failed to store response"

    except Exception as e:
        logging.error(f"An error occurred in store_response: {e}")
        return False, str(e)


async def handle_miner_response(task_id: str, wallet_address: str, output: bytes):
    try:
        # Find the task by ID
        task = AiTask.find_one({"id": task_id})

        if not task:
            return False, "Task not found"

        # Check if the wallet address is associated with the task
        if task["wallet"] != wallet_address:
            return False, "Task not found or expired"

        print(f'wallet: {task["wallet"]}, passed: {wallet_address} ')

        # Check if the task status is "sent"
        if task["status"] != "sent":
            return False, "Task already completed or invalid status"

        retrieve_id = task["retrieve_id"]
        time = task["time"]
        type = task["type"]

        # If all checks pass, update the task status to "completed" and add the output
        update_result = AiTask.update_one(
            {"id": task_id}, {"$set": {"status": "completed"}}
        )

        if update_result.modified_count > 0:
            try:
                # Call update_validation_task if the task type is "high"
                if type == "high":
                    validation_update, validation_message = update_validation_task(
                        task_id, output, wallet_address
                    )
                    if not validation_update:
                        logging.info(f"{validation_message}")

                # Call the store_response function after successfully updating the task status
                store_success, store_message = await store_response(
                    task_id, wallet_address, output, retrieve_id
                )

                # Calculate the score and update user info
                score = calculate_speed_score(time)
                success, message = upsert_user_info(wallet_address, score)

                if not success:
                    return False, message

                if store_success:
                    return True, "Task Accepted and Response Stored"
                else:
                    return (
                        False,
                        f"Task Accepted but Failed to Store Response: {store_message}",
                    )

            except Exception as store_error:
                return (
                    False,
                    f"Error in storing response or updating user info: {store_error}",
                )

        else:
            return False, "Task Rejected"

    except Exception as e:
        logging.error(f"An error occurred in handle_miner_response: {e}")
        return False, str(e)


# ###########---------------------------------###################################


def calculate_speed_score(task_completion_time_utc):
    try:
        # Convert the input time string to a datetime object using the specified format
        task_completion_time = datetime.strptime(
            task_completion_time_utc, "%Y-%m-%dT%H:%M:%S.%f"
        )

        # Get the current UTC time
        current_time = datetime.utcnow()

        # Calculate the time difference between now and the task completion time in seconds
        time_diff = (current_time - task_completion_time).total_seconds()

        # Calculate the score based on the time difference
        # Full score (10) is given if the task is completed within 6 seconds
        # The score decreases by 1 for every additional 5 seconds
        # The minimum score is 1
        score = max(1, 10 - math.ceil((time_diff - 6) / 5))

        return score

    except Exception as e:
        # Log an error message if an exception occurs and return a score of 0
        logging.error(f"An error occurred in calculate_speed_score: {e}")
        return 0


def upsert_user_info(wallet_address, score=None):
    # Define default values
    default_tp = 50
    default_np = 0
    default_score = 0
    default_balance = 0

    try:
        # Try to find the user
        user = userStats.find_one({"wallet_address": wallet_address})

        if user:
            # Update existing user
            update_doc = {"$set": {"last_active_time": datetime.utcnow()}}
            if score is not None:
                update_doc["$inc"] = {"score": score}

            userStats.update_one({"wallet_address": wallet_address}, update_doc)
            return True, f"User updated with wallet_address: {wallet_address}"

        else:
            # Create new user
            new_user = {
                "wallet_address": wallet_address,
                "last_active_time": datetime.utcnow(),
                "tp": default_tp,
                "np": default_np,
                "score": score if score is not None else default_score,
                "balance": default_balance,
            }
            userStats.insert_one(new_user)
            return True, f"New user created with wallet_address: {wallet_address}"

    except PyMongoError as e:
        return False, f"An error occurred while updating upsert_user_info: {e}"


def add_processed_validator(val_id, validator_address):
    try:
        # Find the document with the given val_id
        query = {"task1.val_id": val_id}
        task = ValidationTask.find_one(query)

        if task:
            # Check if the validator_address is already in the list
            if validator_address not in task.get("task1", {}).get("validators", []):
                # Add the validator_address to the validators list
                updated_validators = task.get("task1", {}).get("validators", []) + [
                    validator_address
                ]

                # Update the document
                update_result = ValidationTask.update_one(
                    query, {"$set": {"task1.validators": updated_validators}}
                )

                if update_result.modified_count == 1:
                    return True

        return False

    except Exception as e:
        logging.error(
            f"An error occurred while adding validator in add_processed_validator: {e}"
        )
        return False


def is_task_valid(val_id: str) -> bool:
    try:
        # Find the document with the given val_id
        query = {"val_id": val_id}
        task = ValidationTaskHistory.find_one(query)

        if not task:
            # If no document is found, return False
            return False

        # Parse the createdAt field
        created_at_str = task.get("createdAt")
        created_at = datetime.fromisoformat(created_at_str)

        # Get the current time
        current_time = datetime.utcnow()

        # Check if more than 1 hour has passed
        if current_time - created_at > timedelta(hours=1):
            return False

        return True

    except Exception as e:
        logging.error(
            f"An error occurred while checking task validity in is_task_valid: {e}"
        )
        return False


def miner_eligibility(wallet_address: str) -> bool:
    try:
        # Find the document with the given wallet_address
        query = {"wallet_address": wallet_address}
        user_stat = userStats.find_one(query)

        if not user_stat:
            # If no document is found, return True
            return True

        # Check the np field
        if user_stat.get("np", 0) > 45:
            return False

        return True

    except Exception as e:
        logging.error(f"An error occurred in miner_eligibility: {e}")
        return False


# ###########---------------------------------###################################


def task_validation_output(wallet_address, tp=None, np=None):
    print("*" * 45)
    print("wallet_address", wallet_address)
    print("TP", tp)
    print("NP", np)
    print("*" * 45)
    try:
        # Find the user by wallet address
        user = userStats.find_one({"wallet_address": wallet_address})
        if not user:
            return False, "Miner not found"

        # Prepare the update document
        update_doc = {"$inc": {}}
        if tp is not None:
            update_doc["$inc"]["tp"] = tp
        if np is not None:
            update_doc["$inc"]["np"] = np

        # If there are no updates to perform, return early
        if not update_doc["$inc"]:
            return False, "No changes to update"

        # Update the user stats
        userStats.update_one({"wallet_address": wallet_address}, update_doc)
        return True, f"User validated with wallet_address: {wallet_address}"
    except Exception as e:
        return False, f"An error occurred in task_validation_output: {e}"


def update_validation_task(task_id, output, wallet_address):
    try:
        # Find the task in the ValidationTask collection
        task = ValidationTask.find_one({"task1.array.id": task_id})

        if not task:
            return False, "ValidationTask  does not exist"

        # Update the specific task within the array
        ValidationTask.update_one(
            {"task1.array.id": task_id},
            {
                "$set": {
                    "task1.array.$.wallet": wallet_address,
                    "task1.array.$.status": "completed",
                    "task1.array.$.output": Binary(output),
                }
            },
        )

        # Check if all tasks in the array are completed
        task = ValidationTask.find_one({"task1.array.id": task_id})
        all_completed = all(
            item["status"] == "completed" for item in task["task1"]["array"]
        )

        if all_completed:
            ValidationTask.update_one(
                {"task1.array.id": task_id}, {"$set": {"task1.condition": "dispatch"}}
            )
            logging.info(f"Task is has been dispatched for validation ")

        return True, "Task updated successfully"

    except Exception as e:
        return False, f"An error occurred in update_validation_task: {e}"


async def generate_validation_task():
    try:
        # Check if the validationTask collection is empty
        if ValidationTask.count_documents({}) == 0:
            # Generate random text for the task
            prompt = generate_random_image_prompt()
            negative_prompt = base["PROMPT"]["NEGATIVE"]
            width = base["PROMPT"]["WIDTH"]
            height = base["PROMPT"]["HEIGHT"]
            seed = random.randint(1, 9223372036854775807)
            seed_str = f"{seed}"
            message_type = "requestedTask"

            # Create the array of tasks
            tasks_array = []
            for _ in range(3):
                unique_id = str(uuid.uuid4())
                val_id = str(uuid.uuid7())
                retrieve_id = str(uuid.uuid4())
                current_time = datetime.utcnow().isoformat()

                task_document = {
                    "id": unique_id,
                    "task": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "seed": seed_str,
                    "time": current_time,
                    "retrieve_id": retrieve_id,
                    "wallet": "",
                    "status": "pending",
                    "type": "high",
                    "message_type": message_type,
                }
                tasks_array.append(task_document)

                validators = []

            # Create the validation task document
            validation_task_document = {
                "task1": {
                    "val_id": val_id,
                    "condition": "pending",
                    "createdAt": current_time,
                    "validators": validators,
                    "array": tasks_array,
                }
            }

            validation_task_History = {
                "val_id": val_id,
                "createdAt": current_time,
            }

            # Insert the validation task document into the validationTask collection
            insert_result = ValidationTask.insert_one(validation_task_document)
            insert_history = ValidationTaskHistory.insert_one(validation_task_History)
            # Check if the insertion was acknowledged by MongoDB
            if insert_result.acknowledged:
                # Insert each task_document into the AiTask collection
                for task in tasks_array:
                    ai_task_document = {
                        "id": task["id"],
                        "task": task["task"],
                        "negative_prompt": task["negative_prompt"],
                        "width": task["width"],
                        "height": task["height"],
                        "seed": task["seed"],
                        "time": task["time"],
                        "retrieve_id": task["retrieve_id"],
                        "wallet": task["wallet"],
                        "status": task["status"],
                        "type": "high",
                        "message_type": task["message_type"],
                    }
                    AiTask.insert_one(ai_task_document)
                return True
            else:
                return False
        else:
            logging.error("ValidationTask collection is not empty. Skipping insertion.")
            return False
    except Exception as e:
        logging.error(f"An error occurred in generate_validation_task: {e}")
        return False


async def select_task_for_validation():
    try:
        # Find the first task
        task = ValidationTask.find_one({})

        if not task:
            print("in here")
            return False, json.dumps({"error": "No tasks found"})

        current_time = datetime.utcnow()
        task_created_at = datetime.strptime(
            task["task1"]["createdAt"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        time_difference = current_time - task_created_at

        timer = base["TIME"]["VALIDATION_DELETE_TIMER"]
        if time_difference > timedelta(minutes=timer):
            print("Time difference is greater than 3 minute")
            if (
                task["task1"]["condition"] == "pending"
                or task["task1"]["condition"] == "dispatch"
            ):
                ValidationTask.delete_one({"_id": task["_id"]})
                return False, json.dumps(
                    {
                        "error": "Task is pending/dispatch for more than 3 minutes, hence deleted"
                    }
                )

        # Check the condition
        if task["task1"]["condition"] != "dispatch":
            return False, json.dumps({"error": "Task condition is not dispatch"})

        # If all checks pass, return the details as JSON

        return True, json.dumps(
            {
                "id": task["task1"]["val_id"],
                "validators": task["task1"]["validators"],
            }
        )

    except Exception as e:
        return False, json.dumps({"error": str(e)})

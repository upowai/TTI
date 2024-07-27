from faker import Faker
from database.mongodb import storeTasks, poolTasks, iNodeTask
from datetime import datetime, timedelta
import uuid_utils as uuid
import json
from pymongo.errors import PyMongoError
import math
import logging
import base64
from bson.binary import Binary
import os

from task.compare import compare_images

faker = Faker()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


async def handle_pool_response(val_id, task_info, pool_wallet, pool_ip, pool_port):
    try:
        print("val_id: ", val_id)
        # print("task_info: ", task_info)
        print("pool_wallet: ", pool_wallet)
        print("pool_ip: ", pool_ip)
        print("pool_port: ", pool_port)

        # Check if val_id already exists
        existing_document = storeTasks.find_one({"val_id": val_id})
        if existing_document:
            return (
                False,
                f"Error: validation task with val_id: {val_id} already exists.",
            )

        # Prepare task_info to include additional fields
        formatted_task_info = [
            {
                "id": task.get("id"),
                "retrieve_id": task.get("retrieve_id"),
                "task": task.get("task"),
                "negative_prompt": task.get("negative_prompt"),
                "width": task.get("width"),
                "height": task.get("height"),
                "seed": task.get("seed"),
                "wallet_address": task.get("wallet_address"),
                "time": datetime.fromisoformat(task.get("time")),
                "status": task.get("status"),
                "type": task.get("type"),
                "output": base64.b64decode(task.get("output")),
            }
            for task in task_info
        ]

        # Insert document
        storeTasks.insert_one(
            {
                "val_id": val_id,
                "pool_wallet": pool_wallet,
                "pool_ip": pool_ip,
                "pool_port": pool_port,
                "task_info": formatted_task_info,
            }
        )

        return True, f"Validation task stored in storeTasks with val_id: {val_id}."

    except Exception as e:
        return False, f"An error occurred in handle_pool_response: {str(e)}"


def save_images_from_task_info(task_info):

    image_folder = "received_images"
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    for i, task in enumerate(task_info):
        if isinstance(task, dict):
            try:
                image_data = task.get("output")
                if isinstance(image_data, bytes):
                    image_filename = os.path.join(image_folder, f"image_{i}.png")
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_data)
                    print(f"Image {i} saved successfully.")
                else:
                    print(f"No valid image data found for task {i}.")
            except (base64.binascii.Error, IOError, KeyError) as e:
                print(f"Failed to save image {i} due to: {e}")
        else:
            print(f"Task {i} is not a dictionary: {task}")


def validate_tasks():
    try:
        # Find the first document in the storeTasks collection
        store_task = storeTasks.find_one()

        if store_task:
            # Extract the necessary info
            val_id = store_task.get("val_id")
            pool_wallet = store_task.get("pool_wallet")
            pool_ip = store_task.get("pool_ip")
            pool_port = store_task.get("pool_port")

            # Get all tasks and image bytes for comparison
            wallet_info = store_task.get("task_info", [])

            # Compare images for all tasks
            results = compare_images(wallet_info)

            # Prepare document for iNodeTask collection
            inode_task = {"val_id": val_id, "pool_wallet": pool_wallet}
            # Insert the document into iNodeTask collection
            iNodeTask.insert_one(inode_task)
            logging.info("added task to iNodeTask")

            if results is None:
                # Delete the store_task from storeTasks collection
                storeTasks.delete_one({"_id": store_task["_id"]})
                return (
                    False,
                    "No valid comparison result. Task deleted from storeTasks.",
                )

            # Check if all results are failed
            all_failed = all(result == "failed" for result in results.values())

            if all_failed:
                # Delete the store_task from storeTasks collection
                storeTasks.delete_one({"_id": store_task["_id"]})
                return (
                    False,
                    "All results are failed. Task deleted from storeTasks without punishing anyone.",
                )

            # Extract unique wallets for tp or np assignment
            unique_wallets = []
            seen_wallets = set()

            for task in wallet_info:
                wallet = task.get("wallet_address")
                if wallet not in seen_wallets:
                    seen_wallets.add(wallet)
                    unique_wallets.append(task)

            # Prepare document for poolTasks collection
            pool_task = {
                "val_id": val_id,
                "pool_ip": pool_ip,
                "pool_port": pool_port,
                "tasks": [],
            }

            # Static numbers for tp and np assignment
            tp_number = 1
            np_number = 1

            for wallet in unique_wallets:
                wallet_address = wallet["wallet_address"]
                result = results[wallet_address]
                task_entry = {"wallet_address": wallet_address, "result": result}

                if result == "passed":
                    task_entry["tp"] = tp_number
                else:
                    task_entry["np"] = np_number

                pool_task["tasks"].append(task_entry)

            # Insert the document into poolTasks collection
            result = poolTasks.insert_one(pool_task)

            if result.acknowledged:
                # Delete the store_task from storeTasks collection
                storeTasks.delete_one({"_id": store_task["_id"]})

                return (
                    True,
                    "Successfully moved from storeTasks to poolTasks",
                )
            else:
                return False, "Failed to insert document into poolTasks."

        else:
            return False, "No Task found to validate"

    except PyMongoError as e:
        return False, f"An error occurred while accessing MongoDB: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred in validate_tasks: {e}"


def find_inode_task():
    try:
        document = iNodeTask.find_one()

        if document:
            return True, document
        else:
            return False, "No task found in iNodeTask."

    except PyMongoError as e:
        return False, f"An error occurred while accessing MongoDB: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred in find_inode_task: {e}"


def find_pool_task():
    try:
        document = poolTasks.find_one()
        if document:
            return True, document
        else:
            return False, "No task found in poolTasks."

    except PyMongoError as e:
        return False, f"An error occurred while accessing MongoDB: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred in find_pool_task: {e}"


def delete_inode_task(val_id):
    try:
        # Define the query based on val_id
        query = {"val_id": val_id}

        # Use find_one_and_delete to find and delete the document
        result = iNodeTask.find_one_and_delete(query)

        if result:
            return True, f"Task with val_id '{val_id}' deleted successfully."
        else:
            return False, f"No task found with val_id '{val_id}'."

    except PyMongoError as e:
        return False, f"An error occurred while accessing MongoDB: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred in delete_inode_task: {e}"


def delete_pool_task(val_id):
    try:
        # Define the query based on val_id
        query = {"val_id": val_id}

        # Use find_one_and_delete to find and delete the document
        result = poolTasks.find_one_and_delete(query)

        if result:
            return True, f"Task with val_id '{val_id}' deleted successfully."
        else:
            return False, f"No task found with val_id '{val_id}'."

    except PyMongoError as e:
        return False, f"An error occurred while accessing MongoDB: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred in delete_pool_task: {e}"

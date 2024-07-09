import requests
from bson import ObjectId
import base64
import json
import hashlib
from fastecdsa import keys, curve, ecdsa
from datetime import datetime, timedelta
from database.mongodb import ValidationTask
from utils.layout import base
import utils.config as config
import logging

# Define the private key for signing
private_key = config.PRIVATEKEY
CURVE = curve.P256

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def hash_data(data):
    # Convert the dictionary to a JSON string
    json_data = json.dumps(data, sort_keys=True).encode("utf-8")
    # Create a SHA-256 hash of the JSON string
    return hashlib.sha256(json_data).hexdigest()


def sign_data(hash_str, private_key):
    return ecdsa.sign(hash_str, private_key, curve=CURVE)


def upload_images_to_endpoint(endpoint_url):
    try:
        # Retrieve the document
        document = ValidationTask.find_one()
        if not document:
            return False, json.dumps({"status": False, "message": "No tasks found"})

        current_time = datetime.utcnow()
        task_created_at = datetime.strptime(
            document["task1"]["createdAt"], "%Y-%m-%dT%H:%M:%S.%f"
        )

        time_difference = current_time - task_created_at

        timer = base["TIME"]["VALIDATION_DELETE_TIMER"]
        if time_difference > timedelta(minutes=timer):
            logging.info(f"Time difference is greater than {timer} minutes")
            if (
                document["task1"]["condition"] == "pending"
                or document["task1"]["condition"] == "dispatch"
            ):
                ValidationTask.delete_one({"_id": document["_id"]})
                return False, json.dumps(
                    {
                        "error": f"Task is pending/dispatch for more than {timer} minutes, hence deleted"
                    }
                )

        # Check the condition
        if document["task1"]["condition"] != "dispatch":
            return False, json.dumps({"error": "Task condition is not dispatch"})

        # Extract tasks from the array
        tasks = document.get("task1", {}).get("array", [])

        # Prepare the main data dictionary
        data = {
            "val_id": document.get("task1", {}).get("val_id"),
            "pool_ip": base["POOL_VALIDATION_SOCKET"]["IP"],
            "pool_port": base["POOL_VALIDATION_SOCKET"]["PORT"],
            "pool_wallet": base["POOL_WALLETS"]["POOL_ADDRESS"],
            "condition": document.get("task1", {}).get("condition"),
            "createdAt": document.get("task1", {}).get("createdAt"),
            "tasks": [],
        }

        # Prepare data for signing (excluding output)
        sign_data_dict = {
            "val_id": data["val_id"],
            "pool_ip": data["pool_ip"],
            "pool_port": data["pool_port"],
            "pool_wallet": data["pool_wallet"],
            "condition": data["condition"],
            "createdAt": data["createdAt"],
            "tasks": [],
        }

        # Loop through each task and add to the data dictionary
        for task in tasks:
            task_id = task.get("id")
            task_output = task.get("output")  # This should be the binary image data

            if not task_output:
                print(f"No output for task {task_id}")
                continue

            # Encode the image data to base64
            task_output_base64 = base64.b64encode(task_output).decode("utf-8")

            # Create a task dictionary excluding the output for signing
            task_data_for_signing = {
                "id": task_id,
                "retrieve_id": task.get("retrieve_id"),
                "task": task.get("task"),
                "negative_prompt": task.get("negative_prompt"),
                "wallet_address": task.get("wallet"),
                "width": task.get("width"),
                "height": task.get("height"),
                "seed": task.get("seed"),
                "time": task.get("time"),
                "status": task.get("status"),
                "type": task.get("type"),
                "message_type": task.get("message_type"),
            }

            # Create a task dictionary including the output for uploading
            task_data = task_data_for_signing.copy()
            task_data["output"] = task_output_base64

            # Add the task-specific data to the lists
            sign_data_dict["tasks"].append(task_data_for_signing)
            data["tasks"].append(task_data)

        # Hash the data for signing
        hash_str = hash_data(sign_data_dict)

        # Sign the hash
        r, s = sign_data(hash_str, private_key)

        # Convert r and s to strings and combine them
        signature = f"{r},{s}"

        # Add the signature to the data
        data["signature"] = signature
        data["hash_str"] = hash_str

        endpoint_url = f"{endpoint_url}/upload_tasks/"

        # Upload the data to the endpoint
        response = requests.post(endpoint_url, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors

        return True, response.json()

    except requests.exceptions.RequestException as e:
        return False, json.dumps({"status": False, "message": str(e)})
    except Exception as e:
        return False, json.dumps({"status": False, "message": str(e)})

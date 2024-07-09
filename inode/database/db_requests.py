from pymongo import errors
from database.mongodb import poolList, validatorsList
from bson.json_util import dumps


def add_pool(pool_address: str) -> dict:
    try:

        # Check if the pool_address already exists
        existing_pool = poolList.find_one({"pool_address": pool_address})
        if existing_pool:
            return {"status": "error", "message": "Pool address already exists"}

        # Insert the new pool address
        result = poolList.insert_one({"pool_address": pool_address})
        return {
            "status": "success",
            "message": "Pool added successfully",
            "pool_id": str(result.inserted_id),
        }

    except errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}


def remove_pool(pool_address: str) -> dict:
    try:

        # Remove the pool address
        result = poolList.delete_one({"pool_address": pool_address})

        if result.deleted_count == 0:
            return {"status": "error", "message": "Pool address not found"}

        return {"status": "success", "message": "Pool removed successfully"}

    except errors.PyMongoError as e:
        return {"status": "error", "message": str(e)}


def get_validators_list():
    try:

        # Fetch all documents from the collection
        documents = validatorsList.find()

        # Initialize an empty dictionary to store the results
        results = {}

        # Iterate over the documents and format the results
        for doc in documents:
            wallet_address = doc["wallet_address"]
            doc.pop("_id")  # Remove the MongoDB object ID
            doc.pop("lastFetch")
            doc.pop("wallet_address")  # Remove the wallet_address
            json_str = dumps(doc)  # Convert the document to JSON string
            results[wallet_address] = json_str

        return results

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def get_pools_list():
    try:
        # Fetch all documents from the collection
        documents = poolList.find()

        # Initialize a set to store the pool addresses
        pool_addresses = set()

        # Iterate over the documents and extract the pool addresses
        for doc in documents:
            wallet_address = doc["pool_address"]
            pool_addresses.add(wallet_address)

        return pool_addresses

    except Exception as e:
        print(f"An error occurred: {e}")
        return set()

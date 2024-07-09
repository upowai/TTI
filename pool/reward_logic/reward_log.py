import json
import json
from bson import json_util
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)
from database.mongodb import rewardLog


def store_in_db(block_height, updates):
    if rewardLog is None:
        logging.info("Database collection not initialized.")
        return

    if not isinstance(block_height, str) or not isinstance(updates, dict):
        logging.error("Invalid input types for block_height or miner_updates.")
        return

    if not updates:
        logging.info("Empty updates. Nothing to store.")
        return

    try:
        existing_document = rewardLog.find_one({"block_height": block_height})
        if existing_document:
            logging.info(
                f"Block height {block_height} already exists. Consider updating it instead of inserting a new one."
            )
            return

        document = {"block_height": block_height, "updates": updates}
        rewardLog.insert_one(document)
        logging.info(f"Successfully stored updates for block height {block_height}.")
    except Exception as e:
        logging.error(
            f"Error storing data in MongoDB for block height {block_height}: {e}"
        )


def retrieve_from_db(block_height):
    if rewardLog is None:
        logging.info("Database collection not initialized.")
        return None
    try:
        document = rewardLog.find_one({"block_height": block_height})

        if document:
            json_str = json.dumps(document, default=json_util.default, indent=4)
            logging.info(
                f"Successfully retrieved updates for block height {block_height}."
            )
            return json_str
        else:
            logging.info(f"No updates found for block height {block_height}.")
            return None
    except Exception as e:
        logging.error(
            f"Error retrieving data from MongoDB for block height {block_height}: {e}"
        )
        return None

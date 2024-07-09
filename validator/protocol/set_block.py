from database.mongodb import blockHeight
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def set_last_block_height(block_height):
    try:
        # Ensure block_height is an integer to prevent data type issues
        block_height = int(block_height)
        result = blockHeight.update_one(
            {"_id": "last_block_height"},
            {"$set": {"block_height": block_height}},
            upsert=True,
        )
        if result.modified_count > 0 or result.upserted_id:
            logging.info(f"Block height set to {block_height}.")
            return True
        return False
    except ValueError:
        logging.error("Invalid block_height type. Expected an integer.")
    except Exception as e:
        logging.error(f"Unexpected error setting last block height: {e}")
    return False


def get_last_block_height():
    try:
        doc = blockHeight.find_one({"_id": "last_block_height"})
        if doc is None:
            return None
        return int(doc["block_height"])
    except ValueError:
        logging.error("Stored 'last_block_height' is not an integer.")
    except Exception as e:
        logging.error(f"Unexpected error retrieving last block height: {e}")
    return None

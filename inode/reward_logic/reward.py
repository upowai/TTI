from pymongo.errors import PyMongoError
from datetime import datetime, timedelta
import math
from database.mongodb import poolList, validatorsList, minerPool


import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def find_pool(pool_address):

    try:
        result = poolList.find_one({"pool_address": pool_address})
        if result:
            return True, f"Pool found: {result}"
        else:
            return False, "Pool not registered."
    except PyMongoError as e:
        return False, f"Error occurred in find_pool: {e}"


def get_validator_percentage(validator_address):
    try:
        result = validatorsList.find_one(
            {"wallet_address": validator_address}, {"_id": 0, "percentage": 1}
        )
        if result and "percentage" in result:
            percentage = result["percentage"]
            if percentage < 1:
                return (
                    False,
                    "Validator does not have enough percentage to be a validator.",
                )
            else:
                return True, percentage
        else:
            return False, "Validator not found"
    except PyMongoError as e:
        return False, f"Error occurred in get_validator_percentage: {e}"


def set_pool_score(pool_address, validator_address):
    MAX_SCORE = 100
    SCORE_INCREMENT_MAX = 20  # The max increment 100%

    # Check if the pool exists
    success, message = find_pool(pool_address)
    if not success:
        return False, message

    # Get the validator percentage
    success, result = get_validator_percentage(validator_address)
    if not success:
        return False, result
    percentage = result

    try:
        # Calculate score increment
        score_increment = math.ceil((percentage / 100) * SCORE_INCREMENT_MAX)
        # Ensure the score increment is at least 1
        score_increment = max(score_increment, 1)

        # Atomically fetch and update the score
        current_pool = minerPool.find_one({"pool_address": pool_address})
        if current_pool:
            current_score = current_pool.get("score", 0)
            new_score = min(MAX_SCORE, current_score + score_increment)
            update_result = minerPool.update_one(
                {"pool_address": pool_address},
                {
                    "$set": {
                        "score": new_score,
                        "last_active_time": datetime.utcnow(),
                    }
                },
                upsert=True,
            )
        else:
            new_score = score_increment
            update_result = minerPool.update_one(
                {"pool_address": pool_address},
                {
                    "$set": {
                        "score": new_score,
                        "last_active_time": datetime.utcnow(),
                    }
                },
                upsert=True,
            )

        if update_result.modified_count > 0 or update_result.upserted_id is not None:
            logging.info(f"Made a score update for pool: {pool_address}")
            return True, f"Score updated to {new_score}."
        else:
            return False, "Failed to update score."
    except PyMongoError as e:
        return False, f"Error occurred in set_pool_score: {e}"


def set_validator_score(validator_address):
    try:
        # Check if the validator exists
        validator = validatorsList.find_one({"wallet_address": validator_address})
        if not validator:
            return False, f"Validator with address {validator_address} does not exist."

        current_time_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        # Update the validator's score
        update_result = validatorsList.update_one(
            {"wallet_address": validator_address},
            {"$set": {"score": 1, "last_active_time": current_time_str}},
        )

        if update_result.modified_count > 0:
            logging.info(f"Made a score update for validator: {validator_address}")
            return True, "Validator score updated."
        else:
            return False, "Failed to update validator score."
    except PyMongoError as e:
        return False, f"Error occurred while updating set_validator_score: {e}"
    except ValueError as ve:
        return False, str(ve)


def decay_pool_score():
    try:
        # Retrieve all entries in the minerPool collection
        all_miners = minerPool.find()

        for miner in all_miners:
            pool_address = miner["pool_address"]
            current_score = miner.get("score", 0)

            # Skip if the current score is 0
            if current_score <= 0:
                print(f"Score for pool {pool_address} is already 0, skipping.")
                continue

            # Calculate 10% of the current score
            score_decrement = math.ceil(0.10 * current_score)
            new_score = max(current_score - score_decrement, 0)

            # Update the score in the database
            update_result = minerPool.update_one(
                {"pool_address": pool_address},
                {
                    "$set": {"score": new_score},
                },
            )

            if update_result.modified_count > 0:
                logging.info(
                    f"Score for pool {pool_address} decay from {current_score} to {new_score}."
                )
            else:
                logging.info(f"Failed to update score for pool {pool_address}.")

        return True, "Scores updated for all pools."
    except PyMongoError as e:
        return False, f"Error occurred in decay_pool_score: {e}"


def decay_validator_score():
    try:
        # Retrieve all entries in the validators collection
        all_validators = validatorsList.find()

        for validators in all_validators:
            validator_address = validators["wallet_address"]
            current_score = validators.get("score", 0)

            # Skip if the current score is 0
            if current_score <= 0:
                logging.info(
                    f"Score for validator {validator_address} is already 0, skipping."
                )
                continue

            score = 0

            # Update the score in the database
            update_result = validatorsList.update_one(
                {"wallet_address": validator_address},
                {
                    "$set": {"score": score},
                },
            )

            if update_result.modified_count > 0:
                logging.info(
                    f"Score for validator {validator_address} decay from {current_score} to {score}."
                )
            else:
                logging.info(
                    f"Failed to update score for validator {validator_address}."
                )

        return True, "Scores updated for all validators."
    except PyMongoError as e:
        return False, f"Error occurred in decay_validator_score: {e}"


def update_scores(pool_address, validator_address):
    try:
        # Update pool score
        pool_success, pool_message = set_pool_score(pool_address, validator_address)
        if not pool_success:
            return False, f"Pool score update failed: {pool_message}"

        # Update validator score
        validator_success, validator_message = set_validator_score(validator_address)
        if not validator_success:
            return False, f"Validator score update failed: {validator_message}"

        return True, "scores updated successfully for pool and validators."

    except Exception as e:
        return False, f"Error occurred in update_scores: {str(e)}"

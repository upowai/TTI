from pymongo.errors import ConnectionFailure
from database.mongodb import validatorsList
from api.api_client import fetch_validators
from utils.layout import base
from datetime import datetime


def update_validators_list():
    try:
        fetch_url = (
            f'{base["URLS"]["VALIDATORS_URL"]}{base["INODE_WALLETS"]["WALLET_ADDRESS"]}'
        )
        validator_data = fetch_validators(fetch_url)
        total_stake_all_validators = sum(
            validator.get("totalStake", 0) for validator in validator_data[:60]
        )
        for validator in validator_data[:60]:
            wallet_address = validator.get("validator")
            votes = validator.get("vote", [])
            totalStake = validator.get("totalStake", 0)

            # Summing up all vote counts for the validator
            vote_count_sum = sum(vote.get("vote_count", 0) for vote in votes)

            # Fetch the current details from MongoDB
            validator_details = validatorsList.find_one(
                {"wallet_address": wallet_address}
            )
            if validator_details:
                details = validator_details
            else:
                details = {
                    "wallet_address": wallet_address,
                    "balance": 0,
                    "score": 0,
                    "ping": "0",
                    "ip": "0",
                    "port": 0,
                    "vote": vote_count_sum,
                    "totalStake": totalStake,
                    "lastFetch": datetime.utcnow(),
                }

            details["vote"] = vote_count_sum
            details["totalStake"] = totalStake
            details["lastFetch"] = datetime.utcnow()
            if total_stake_all_validators > 0:
                percentage_stake = round(
                    (totalStake / total_stake_all_validators) * 100, 2
                )
                details["percentage"] = percentage_stake

            # Update the document in MongoDB
            validatorsList.update_one(
                {"wallet_address": wallet_address}, {"$set": details}, upsert=True
            )
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
    except Exception as e:
        print(f"update_validators_list An error occurred: {e}")


def update_validator_info(wallet_address, new_ip, new_port, validator_endpoint):
    try:
        query = {"wallet_address": wallet_address}
        wallet_doc = validatorsList.find_one(query)

        if not wallet_doc:
            return False, "Wallet address not found."

        current_time_str = datetime.utcnow().isoformat()

        # Update the document with new_ip, new_port, and current UTC time in ping
        update_data = {
            "$set": {
                "ip": new_ip,
                "port": new_port,
                "validator_endpoint": validator_endpoint,
                "ping": current_time_str,
            },
        }

        # Perform the update
        result = validatorsList.update_one(query, update_data)

        if result.modified_count > 0:
            return True, "Validator Ping updated."
        else:
            return False, "Failed to update."

    except Exception as e:
        return False, f"An error occurred in update_validator_info: {str(e)}"

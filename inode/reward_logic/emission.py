from decimal import Decimal
from reward_logic.reward_log import store_in_db
from reward_logic.percentage import round_up_decimal_new
from database.mongodb import validatorsList, minerPool
from transaction.payment import add_transaction_to_batch
from utils.layout import base
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def convert_decimal_to_float(data):
    if isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(i) for i in data]
    elif isinstance(data, Decimal):
        return float(data)
    else:
        return data


def pool_emission(amount, block_range, batch_size=1000):
    amount = Decimal(amount)
    pool_updates = {}

    try:
        total_score = Decimal(0)
        cursor = minerPool.find({"score": {"$gt": 0}})
        filtered_pools = []

        # Calculate total score
        for pool_data in cursor:
            score = Decimal(pool_data.get("score", 0))
            filtered_pools.append(pool_data)
            total_score += score

        if not filtered_pools:
            logging.info("No pools found with a positive score.")
            return False, "No pools found with a positive score."

        if total_score == 0:
            logging.info("Total score is zero; no balances updated.")
            return False, "Total score is zero; no balances updated."

        # Process pools in batches
        for i in range(0, len(filtered_pools), batch_size):
            batch = filtered_pools[i : i + batch_size]
            for all_pool_data in batch:
                score = Decimal(all_pool_data.get("score", 0))
                miner_share = (score / total_score) * amount
                miner_share = round_up_decimal_new(miner_share)

                pool_updates[all_pool_data["pool_address"]] = {
                    "score": float(score),
                    "amount": float(miner_share),
                }

                try:
                    add_transaction_to_batch(
                        all_pool_data["pool_address"],
                        float(miner_share),
                        "pool_reward",
                    )
                except Exception as e:
                    logging.error(f"Error processing pool reward distribution: {e}")
                    return False, f"Error processing pool reward distribution: {e}"

        # Convert all Decimal values to float before storing
        pool_updates = convert_decimal_to_float(pool_updates)

        # Store updates in the DB (external function)
        store_in_db(block_range, pool_updates)

        logging.info("Pool transactions are added")
        return True, "Pool balances processed successfully."

    except Exception as e:
        logging.error(f"pool_emission: An unexpected error occurred: {e}")
        return False, f"An unexpected error occurred: {e}"


def validator_emission(amount, batch_size=1000):
    amount = Decimal(amount)
    try:
        cursor = validatorsList.find({"score": 1})
        filtered_validators = []

        # Collect eligible validators
        for validator_data in cursor:
            filtered_validators.append(validator_data)

        if not filtered_validators:
            logging.info("No validators found with a score of 1.")
            return False, "No validators found with a score of 1."

        # Process validators in batches
        for i in range(0, len(filtered_validators), batch_size):
            batch = filtered_validators[i : i + batch_size]
            for validator_data in batch:
                percentage = Decimal(validator_data.get("percentage", 0))
                validator_share = (
                    percentage / 100
                ) * amount  # Calculate share by percentage
                validator_share = round_up_decimal_new(validator_share)

                try:
                    add_transaction_to_batch(
                        validator_data["wallet_address"],
                        float(validator_share),
                        "validator_reward",
                    )
                except Exception as e:
                    logging.error(
                        f"Error processing Validator reward distribution: {e}"
                    )
                    return (
                        False,
                        f"Error processing Validator reward distribution: {e}",
                    )

        logging.info("Validator transactions are added.")
        return True, "Validator balances processed successfully."

    except Exception as e:
        logging.error(f"validator_emission: An unexpected error occurred: {e}")
        return False, f"An unexpected error occurred: {e}"


def iNode_emission(amount):
    try:
        amount = Decimal(amount)
        iNode_share = round_up_decimal_new(amount)
        try:
            add_transaction_to_batch(
                base["INODE_WALLETS"]["REWARD_ADDRESS"],
                float(iNode_share),
                "iNode_reward",
            )
            return True, f"iNode reward has been  processed successfully."
        except Exception as e:
            logging.error(f"Error processing iNode reward distribution: {e}")
            return False, f"Error processing iNode reward distribution: {e}"
    except Exception as e:
        logging.error(f"iNode_emission: An unexpected error occurred: {e}")
        return False, f"An unexpected error occurred: {e}"

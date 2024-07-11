from database.mongodb import blockTransactions
from utils.layout import base
from pymongo.errors import PyMongoError
from protocol.set_block import get_last_block_height, set_last_block_height
from api.api_client import fetch_block
from reward_logic.percentage import calculate_percentages, percentage_match
from reward_logic.miner_reward import update_miner_balances
from reward_logic.pool_reward import update_pool_reward
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def record_block_transactions(hash_value):
    try:
        result = blockTransactions.update_one(
            {"hash": hash_value},
            {"$setOnInsert": {"hash": hash_value}},
            upsert=True,
        )
        if result.upserted_id is not None:
            # logging.info(f"Inserted new transaction with hash: {hash_value}")
            return True
        else:
            logging.info(f"Transaction with hash: {hash_value} already exists.")
            return False
    except PyMongoError as e:
        logging.error(
            f"Failed to insert or check transaction with hash: {hash_value}. Error in record_block_transactions: {e}"
        )
        return None


def analyze_block_rewards():
    output = percentage_match()
    if output is False:
        logging.info(f"Some issue with AWARD_SYSTEM")
        return None
    try:
        last_block_height = get_last_block_height()

        if last_block_height is None:
            logging.info("No last block height found in db, using hardcoded value.")
            last_block_height = base["REWARD_TRACKING"]["BLOCK_HEIGHT"]
        else:
            last_block_height += 1

        logging.info(
            f"Tracking blocks in bulk from height {last_block_height} to {last_block_height+4}"
        )

        data = fetch_block(
            f"{base['URLS']['API_URL']}/get_blocks_details?offset={last_block_height}&limit=5"
        )

        if data is None or not data["result"]:
            logging.error("No new blocks retrieved since the last check.")
            return None

        total_amount = 0
        first_block_id = data["result"][0]["block"]["id"]
        last_block_idX = data["result"][-1]["block"]["id"]
        last_block_id = None

        # Fetch current real block height
        current_block_height_data = fetch_block(
            f"{base['URLS']['API_URL']}/get_supply_info"
        )

        if (
            current_block_height_data is None
            or "result" not in current_block_height_data
        ):
            logging.error("Unable to fetch current block height.")
            return None

        current_block_height = current_block_height_data["result"]["last_block"]["id"]

        if current_block_height < last_block_idX + 5:
            needed_block_height = last_block_height + 9
            logging.info(
                f"Waiting for 5 blocks to confirm from block {last_block_height+4}. Current height: {current_block_height}. Needed: {needed_block_height}."
            )

            return None

        for block in data["result"]:
            block_id = block["block"]["id"]
            last_block_id = block_id

            for transaction in block["transactions"]:
                hash_value = transaction["hash"]
                transaction_amount = 0  # Initialize transaction amount

                if transaction.get("transaction_type", "REGULAR") != "REGULAR":
                    continue

                # Collect all input addresses for the current transaction
                input_addresses = [
                    input["address"] for input in transaction.get("inputs", [])
                ]

                # Check if the transaction is relevant and calculate its amount
                for output in transaction["outputs"]:
                    # Check if the output is for the miner pool wallet address, the type is REGULAR, and the output address is not in the transaction's input addresses (not a self-transaction)
                    if (
                        output["address"] == base["POOL_WALLETS"]["POOL_ADDRESS"]
                        and output["type"] == "REGULAR"
                        and output["address"] not in input_addresses
                    ):
                        transaction_amount += output["amount"]

                # Only proceed if the transaction is relevant and not already recorded
                if transaction_amount > 0:
                    if record_block_transactions(hash_value):
                        # Add the transaction amount only if it's a new transaction
                        total_amount += transaction_amount
                    else:
                        logging.info(
                            f"Skipping already processed transaction: {hash_value}"
                        )

        if last_block_id is not None:
            set_last_block_height(last_block_id)
        else:
            logging.info("No new blocks to process.")

        if total_amount <= 0:
            logging.info(
                f'No relevant transactions found for {base["POOL_WALLETS"]["POOL_ADDRESS"]} in the latest blocks.'
            )
            return None

        percentages = calculate_percentages(total_amount)
        block_range_str = f"{first_block_id}-{last_block_idX}"

        # print("percentages", percentages, "total_amount", total_amount)

        return percentages, block_range_str

    except Exception as e:
        logging.error(f"An error occurred during analyze_block_rewards: {e}")
        return None


def process_block_rewards():
    try:
        info = analyze_block_rewards()
        if info is not None:
            percentages, block_range_str = info
            update_miner_balances(percentages["82%"], block_range_str)
            update_pool_reward(percentages["18%"])
            logging.info(f'All miners Reward: {percentages["82%"]} ')
            logging.info(f'Pool Reward: {percentages["18%"]} ')
        else:
            logging.info("Skipping rewards for everyone")
    except ValueError as e:
        logging.error(f"Error fetching block data: {e}")
    except Exception as e:
        logging.error(f"process_block_rewards An unexpected error occurred: {e}")

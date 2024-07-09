from database.mongodb import blockTransactions
from utils.layout import base
from pymongo.errors import PyMongoError
from api.delegates import fetch_all_delegate_info, sort_delegates
from reward_logic.delegates_reward import update_delegate_balances
from reward_logic.val_reward import update_entityOwners_reward
from protocol.set_block import get_last_block_height, set_last_block_height
from api.api_client import fetch_block
from reward_logic.percentage import calculate_percentages, percentage_match
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
        logging.info(f"Some issue with validator AWARD_SYSTEM")
        return None
    try:
        last_block_height = get_last_block_height()

        if last_block_height is None:
            logging.info("No last block height found in db, using hardcoded value.")
            last_block_height = base["REWARD_TRACKING"]["BLOCK_HEIGHT"]
        else:
            last_block_height += 1

        logging.info(f"Starting processing from block height: {last_block_height}")

        data = fetch_block(
            f"{base['URLS']['API_URL']}/get_blocks_details?offset={last_block_height}&limit=10"
        )

        if data is None or not data["result"]:
            logging.error("No block data retrieved or no new blocks since last check.")
            return None

        total_amount = 0
        first_block_id = data["result"][0]["block"]["id"]
        last_block_idX = data["result"][-1]["block"]["id"]
        last_block_id = None

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
                        output["address"] == base["VALIDATOR_WALLETS"]["VAL_ADDRESS"]
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
                f'No relevant transactions found for {base["VALIDATOR_WALLETS"]["VAL_ADDRESS"]} in the latest blocks.'
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
        sorted_delegates = None
        try:
            delegates_info = fetch_all_delegate_info(
                base["URLS"]["API_URL"], base["VALIDATOR_WALLETS"]["VAL_ADDRESS"]
            )
            if delegates_info:
                sorted_delegates = sort_delegates(delegates_info)
            else:
                logging.error("Failed to fetch delegate information.")
            info = analyze_block_rewards()
            if info is not None:
                percentages, block_range_str = info
                update_delegate_balances(
                    percentages["82%"], sorted_delegates, block_range_str
                )
                update_entityOwners_reward(percentages["18%"])
                logging.info(f'All delegates Reward: {percentages["82%"]} ')
                logging.info(f'Validator Reward: {percentages["18%"]} ')
            else:
                logging.info("Skipping rewards for delegates and validator")
        except ValueError as e:
            logging.error(f"Error fetching block data: {e}")
        except Exception as e:
            logging.error(f"process_block_rewards An unexpected error occurred: {e}")
    except Exception as e:
        logging.error(f"process_block_rewards An unexpected error occurred: {e}")

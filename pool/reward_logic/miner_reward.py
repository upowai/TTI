import logging
import json
from datetime import datetime
from reward_logic.reward_log import store_in_db, retrieve_from_db
from reward_logic.percentage import round_up_decimal_new
from database.mongodb import userStats
from decimal import Decimal

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


def update_miner_balances(amount, block_range, batch_size=1000):
    amount = Decimal(amount)
    miner_updates = {}

    try:
        total_score = Decimal(0)
        cursor = userStats.find({"score": {"$gt": 0}})
        filtered_miners = []

        # Calculate total score
        for miner_data in cursor:
            score = Decimal(miner_data.get("score", 0))
            filtered_miners.append(miner_data)
            total_score += score

        if total_score == 0:
            logging.info("No miners have a positive score; no balances updated.")
            return

        # Process miners in batches
        for i in range(0, len(filtered_miners), batch_size):
            batch = filtered_miners[i : i + batch_size]
            for miner_data in batch:
                previous_balance = Decimal(miner_data.get("balance", 0))
                score = Decimal(miner_data.get("score", 0))
                miner_share = (score / total_score) * amount
                miner_share = round_up_decimal_new(miner_share)
                current_balance = round_up_decimal_new(previous_balance + miner_share)

                # Update the miner's document in MongoDB (convert Decimal to float)
                result = userStats.update_one(
                    {"wallet_address": miner_data["wallet_address"]},
                    {"$set": {"balance": float(current_balance), "score": 0}},
                )

                miner_updates[miner_data["wallet_address"]] = {
                    "previous_balance": float(previous_balance),
                    "score": float(score),
                    "added_amount": float(miner_share),
                    "current_balance": float(current_balance),
                }

        # Convert all Decimal values to float before storing
        miner_updates = convert_decimal_to_float(miner_updates)

        # Store updates in the DB (external function)
        store_in_db(block_range, miner_updates)

        logging.info("Balances updated and scores are reset.")

    except Exception as e:
        logging.error(f"update_miner_balances An unexpected error occurred: {e}")

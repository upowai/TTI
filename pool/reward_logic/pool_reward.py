import logging
import json
from datetime import datetime
from reward_logic.reward_log import store_in_db, retrieve_from_db
from reward_logic.percentage import round_up_decimal_new
from database.mongodb import entityOwners
from decimal import Decimal
from utils.layout import base

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


def update_pool_reward(amount):
    amount = Decimal(amount)
    try:
        pool_owner_data = entityOwners.find_one({"_id": "entityOwners"})

        if pool_owner_data:
            current_amount = Decimal(str(pool_owner_data.get("amount", "0.0")))
            wallet_address = pool_owner_data.get(
                "wallet_address", base["POOL_WALLETS"]["POOL_REWARD_ADDRESS"]
            )
        else:
            current_amount = Decimal("0.0")
            wallet_address = base["POOL_WALLETS"]["POOL_REWARD_ADDRESS"]

        new_amount = round_up_decimal_new(current_amount + amount)
        current_time_utc = datetime.utcnow().isoformat()

        entityOwners.update_one(
            {"_id": "entityOwners"},
            {
                "$set": {
                    "amount": float(new_amount),
                    "last_processed": current_time_utc,
                    "wallet_address": wallet_address,
                }
            },
            upsert=True,
        )

    except Exception as e:
        logging.error(f"update_pool_reward An unexpected error occurred: {e}")

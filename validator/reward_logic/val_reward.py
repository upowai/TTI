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


def update_entityOwners_reward(amount):
    amount = Decimal(amount)
    try:
        entry = entityOwners.find_one({"_id": "entityOwners"})

        if entry:
            current_amount = Decimal(str(entry.get("amount", "0.0")))
            wallet_address = entry.get(
                "wallet_address", base["VALIDATOR_WALLETS"]["VAL_ADDRESS"]
            )
        else:
            current_amount = Decimal("0.0")
            wallet_address = base["VALIDATOR_WALLETS"]["VAL_ADDRESS"]

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
        logging.error(f"update_val_reward An unexpected error occurred: {e}")

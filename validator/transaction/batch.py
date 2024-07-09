import logging
import asyncio
from datetime import datetime
from decimal import Decimal
from utils.layout import base
from api.api_client import test_api_connection
from database.mongodb import tempWithdrawals

from transaction.payment import sign_and_push_transactions

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def process_all_transactions():
    if not test_api_connection(base["URLS"]["API_URL"]):
        logging.warning("Blockchain may be down, no transactions pushed.")
        return
    try:

        all_transactions = list(tempWithdrawals.find().sort("timestamp", 1))

        unique_transactions = {}
        for transaction in all_transactions:
            wallet_address = transaction["wallet_address"]
            unique_transactions[wallet_address] = transaction

        pending_transactions = list(unique_transactions.values())[:15]

        if pending_transactions:
            # Since sign_and_push_transactions is an async function,
            # we need to run it inside an event loop
            asyncio.run(sign_and_push_transactions(pending_transactions))

        else:
            print("No pending transactions to process.")
    except Exception as e:
        print(f"Error during process_all_transactions_mongodb: {e}")

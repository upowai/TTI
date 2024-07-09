import asyncio
import upowpy as upow
import upowpy.utils as upow_utils
import logging
from decimal import Decimal
from datetime import datetime
import utils.config as config
from api.api_client import test_api_connection
import uuid_utils as uuid

from database.mongodb import (
    tempWithdrawals,
    submittedTransactions,
    verifiedTransactions,
    errorTransactions,
    catchTransactions,
)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


utils_instance = upow_utils.Utils()
utils_instance.set_node_url("https://api.upow.ai")


def round_up_decimal_new(decimal: Decimal, round_up_length: str = "0.00000001"):
    round_up_length = Decimal(round_up_length)
    decimal = decimal.quantize(round_up_length)
    return decimal


async def sign_and_push_transactions(transactions):
    try:
        for transaction in transactions:
            private_key = config.PRIVATEKEY
            wallet_address = transaction.get("wallet_address")
            transaction_type = transaction.get("type")
            id = transaction.get("id")
            new_balance = transaction.get("new_balance")
            amounts = "{:.8f}".format(float(new_balance))

            message = ""
            try:
                transaction_hash = await upow.send_transaction(
                    utils_instance, private_key, wallet_address, amounts, message
                )
                if transaction_hash:
                    logging.info(f"transaction_hash: {transaction_hash}")
                    submittedTransactions.update_one(
                        {"wallet_address": wallet_address},
                        {
                            "$push": {
                                "transactions": {
                                    "id": id,
                                    "hash": transaction_hash,
                                    "amount": amounts,
                                    "timestamp": datetime.utcnow(),
                                    "transaction_type": transaction_type,
                                }
                            }
                        },
                        upsert=True,
                    )
                    tempWithdrawals.delete_one({"id": id})
                else:
                    logging.error(
                        f"Transaction failed for wallet address {wallet_address}. No hash was returned."
                    )
                    errorTransactions.update_one(
                        {"wallet_address": wallet_address},
                        {
                            "$push": {
                                "transactions": {
                                    "id": id,
                                    "error": transaction_hash,
                                    "amount": amounts,
                                    "timestamp": datetime.utcnow(),
                                }
                            }
                        },
                        upsert=True,
                    )
            except Exception as e:
                error_message = str(e)
                if "You can spend max 255 inputs" in error_message:
                    num_inputs = int(error_message.split("not ")[-1])
                    max_inputs = 255
                    num_splits = -(-num_inputs // max_inputs)  # Ceiling division
                    amount = Decimal(amounts)
                    split_amount = round_up_decimal_new(amount / num_splits)
                    logging.info(
                        f"Splitting transaction for {wallet_address} into {num_splits} parts due to UTXO limit."
                    )
                    for _ in range(num_splits):
                        add_transaction_to_batch(
                            wallet_address,
                            split_amount,
                            f"utxos_split_{transaction_type}",
                        )
                    tempWithdrawals.delete_one({"id": id})
                elif "URI Too Long for url:" in error_message:
                    amount = Decimal(amounts)
                    split_amount = round_up_decimal_new(amount / 2)
                    logging.info(
                        f"Splitting transaction for {wallet_address} into 2 parts due to URI length limit."
                    )
                    for _ in range(2):
                        add_transaction_to_batch(
                            wallet_address,
                            split_amount,
                            f"url_split_{transaction_type}",
                        )

                    tempWithdrawals.delete_one({"id": id})
                elif "Request-URI Too Large for url:" in error_message:
                    amount = Decimal(amounts)
                    split_amount = round_up_decimal_new(amount / 2)
                    logging.info(
                        f"Splitting transaction for {wallet_address} into 2 parts due to Request-URI Too Large for url."
                    )
                    for _ in range(2):
                        add_transaction_to_batch(
                            wallet_address,
                            split_amount,
                            f"Request-URI_{transaction_type}",
                        )

                    tempWithdrawals.delete_one({"id": id})
                else:
                    logging.error(
                        f"Error during transaction processing for {wallet_address}: {error_message}"
                    )
                    catchTransactions.update_one(
                        {"wallet_address": wallet_address},
                        {
                            "$push": {
                                "transactions": {
                                    "id": id,
                                    "error": error_message,
                                    "amount": amounts,
                                    "timestamp": datetime.utcnow(),
                                }
                            }
                        },
                        upsert=True,
                    )
                    add_transaction_to_batch(
                        wallet_address, amounts, f"CatchError_{id}"
                    )
                    tempWithdrawals.delete_one({"id": id})

        # Remove successfully processed transactions from the MongoDB collection
        if transactions:
            transactions_ids = [t.get("id") for t in transactions]
            tempWithdrawals.delete_many({"id": {"$in": transactions_ids}})
    except Exception as e:
        logging.error(f"Error during signing and pushing transactions: {e}")


def add_transaction_to_batch(wallet_address, tokens_to_distribute, rewardType):
    try:
        transaction_document = {
            "id": str(uuid.uuid4()),
            "wallet_address": str(wallet_address),
            "new_balance": float(tokens_to_distribute),
            "timestamp": datetime.utcnow(),
            "type": rewardType,
        }
        tempWithdrawals.insert_one(transaction_document)

    except Exception as e:
        print(f"Error add_transaction_to_batch: {e}")

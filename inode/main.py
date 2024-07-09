import threading
import asyncio
import uvicorn
import sys
import logging
import websockets
import time
from dotenv import load_dotenv
import json

from api.fastapi import app
from api.api_client import test_api_connection
from database.mongodb import test_db_connection
from utils.layout import base
from protocol.protocol import iNode_protocol
from transaction.batch import process_all_transactions
from reward_logic.process_blocks import process_block_rewards
from reward_logic.find_validators import update_validators_list, update_validator_info
from reward_logic.reward import decay_pool_score, decay_validator_score

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def run_fastapi():
    uvicorn.run(
        app,
        host=base["FAST_API"]["FAST_API_URL"],
        port=base["FAST_API"]["FAST_API_PORT"],
    )


async def periodic_process_transactions():
    try:
        while True:
            process_block_rewards()
            await asyncio.sleep(base["TIME"]["CHECK_INTERVAL"])
    except Exception as e:
        print(f"Error in periodic_process_transactions: {e}")


def update_balance_periodically():
    try:
        while True:
            # process_all_transactions()
            time.sleep(base["TIME"]["PUSH_TX"])
    except Exception as e:
        print(f"Error in update_balance_periodically: {e}")


def update_validators_periodically():
    try:
        while True:
            update_validators_list()
            time.sleep(base["TIME"]["FETCH_VALIDATORS"])
    except Exception as e:
        print(f"Error in update_validators_periodically: {e}")


def decay_scores_periodically():
    try:
        while True:
            decay_pool_score()
            decay_validator_score()
            time.sleep(base["TIME"]["DECAY"])
    except Exception as e:
        print(f"Error in decay_scores_periodically: {e}")


async def main():
    start_server = websockets.serve(
        iNode_protocol,
        base["INODE_MAIN_SOCKET"]["IP"],
        base["INODE_MAIN_SOCKET"]["PORT"],
    )
    await start_server
    fastapi_thread = threading.Thread(daemon=True, target=run_fastapi)
    balance_thread = threading.Thread(target=update_balance_periodically, daemon=True)
    fetch_val_thread = threading.Thread(
        target=update_validators_periodically, daemon=True
    )
    scores_thread = threading.Thread(target=decay_scores_periodically, daemon=True)
    fastapi_thread.start()
    fetch_val_thread.start()
    balance_thread.start()
    scores_thread.start()

    periodic_task = asyncio.create_task(periodic_process_transactions())

    try:
        await asyncio.gather(periodic_task)
    except KeyboardInterrupt:
        logging.info("Shutting down iNode due to KeyboardInterrupt.")
    finally:
        logging.info("iNode shutdown process starting.")
        periodic_task.cancel()

        await asyncio.gather(
            periodic_task,
            return_exceptions=True,
        )
        logging.info("iNode shutdown process complete.")


if __name__ == "__main__":
    if not test_db_connection():
        logging.error("Failed to establish MongoDB connection. Exiting...")
        sys.exit(1)
    if not test_api_connection(base["URLS"]["API_URL"]):
        logging.error("Failed to establish API connection. Exiting...")
        sys.exit(2)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down iNode due to KeyboardInterrupt.")

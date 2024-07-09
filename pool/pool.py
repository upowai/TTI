import threading
import asyncio
import uvicorn
import sys
import logging
import websockets
import time

from api.fastapi import app
from api.api_client import test_api_connection
from database.mongodb import test_db_connection
from utils.layout import base
from reward_logic.process_blocks import process_block_rewards
from protocol.protocol import miner_protocol
from transaction.batch import process_all_transactions
from task.task import generate_validation_task


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


async def periodic_gen_validation_task():
    try:
        while True:
            await generate_validation_task()
            await asyncio.sleep(base["TIME"]["GEN_VALIDATION_TASK"])
    except Exception as e:
        print(f"Error in periodic_gen_validation_task: {e}")


def update_balance_periodically():
    try:
        while True:
            # process_all_transactions()
            time.sleep(base["TIME"]["PUSH_TX"])
    except Exception as e:
        print(f"Error in update_balance_periodically: {e}")


async def main():
    start_server = websockets.serve(
        miner_protocol,
        base["POOL_MAIN_SOCKET"]["IP"],
        base["POOL_MAIN_SOCKET"]["PORT"],
    )
    await start_server
    fastapi_thread = threading.Thread(daemon=True, target=run_fastapi)
    fastapi_thread.start()
    await asyncio.sleep(1)
    balance_thread = threading.Thread(target=update_balance_periodically, daemon=True)
    balance_thread.start()

    periodic_task = asyncio.create_task(periodic_process_transactions())
    periodic_validation_task = asyncio.create_task(periodic_gen_validation_task())

    try:
        await asyncio.gather(periodic_task, periodic_validation_task)
    except KeyboardInterrupt:
        logging.info("Shutting down Pool due to KeyboardInterrupt.")
    finally:
        logging.info("Pool shutdown process starting.")
        periodic_task.cancel()
        periodic_validation_task.cancel()
        await asyncio.gather(
            periodic_task,
            periodic_validation_task,
            return_exceptions=True,
        )
        logging.info("Pool shutdown process complete.")


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
        logging.info("Shutting down Pool due to KeyboardInterrupt.")

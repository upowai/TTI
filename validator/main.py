import threading
import asyncio
import uvicorn
import sys
import logging
import websockets
import time
import json

from api.fastapi import app
from api.api_client import test_api_connection
from database.mongodb import test_db_connection
from utils.layout import base
from protocol.protocol import (
    validator_protocol,
    send_task_to_iNode,
    send_ping_to_iNode,
    send_response_to_pool,
)
from task.task import find_inode_task, find_pool_task, validate_tasks
from transaction.batch import process_all_transactions
from reward_logic.process_blocks import process_block_rewards

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


async def periodic_process_validate_task():
    try:
        while True:
            result, message = validate_tasks()
            if result:
                logging.info(f"SUCESS: Validating Task: {result}")
            else:
                logging.info(f"ERROR: {message}")
            await asyncio.sleep(base["TIME"]["VALIDATE_TASK"])
    except Exception as e:
        print(f"Error in periodic_process_validate_task: {e}")


def update_balance_periodically():
    try:
        while True:
            process_all_transactions()
            time.sleep(base["TIME"]["PUSH_TX"])
    except Exception as e:
        print(f"Error in update_balance_periodically: {e}")


async def periodic_send_ping():
    while True:
        ip = base["VALIDATOR_SOCKET"]["SERVER_IP"]
        port = base["VALIDATOR_SOCKET"]["PORT"]
        validator_address = base["VALIDATOR_WALLETS"]["VAL_ADDRESS"]
        validator_endpoint = base["ENDPOINT"]["VALIDATOR_URL"]
        message = json.dumps(
            {
                "type": "PING",
                "ip": ip,
                "port": port,
                "validator_wallet": validator_address,
                "validator_endpoint": validator_endpoint,
            }
        )
        uri = (
            f'ws://{base["INODE_INFO"]["INODE_IP"]}:{base["INODE_INFO"]["INODE_PORT"]}'
        )
        await send_ping_to_iNode(uri, message)
        await asyncio.sleep(base["TIME"]["PING_TIME"])


async def periodic_send_task_to_iNode():
    while True:
        success, result = find_inode_task()
        if success:
            # Ensure result is loaded into JSON if it's not already a dictionary
            if isinstance(result, str):
                result = json.loads(result)

            val_id = result.get("val_id")
            pool_wallet = result.get("pool_wallet")
            validator_wallet = base["VALIDATOR_WALLETS"]["VAL_ADDRESS"]

            # Construct the message
            message = json.dumps(
                {
                    "type": "TASK",
                    "pool_wallet": pool_wallet,
                    "validator_wallet": validator_wallet,
                    "val_id": val_id,
                }
            )

            uri = f'ws://{base["INODE_INFO"]["INODE_IP"]}:{base["INODE_INFO"]["INODE_PORT"]}'
            await send_task_to_iNode(uri, message, val_id)
        await asyncio.sleep(60)


async def periodic_send_task_to_pool():
    while True:
        success, result = find_pool_task()
        if success:
            logging.info("Sending back validated task info to pool")
            # Ensure result is loaded into JSON if it's not already a dictionary
            if isinstance(result, str):
                result = json.loads(result)

            # get tasks and val_id
            tasks = result.get("tasks")
            val_id = result.get("val_id")

            # get ip and port of pool
            ip = result.get("pool_ip")
            port = result.get("pool_port")

            # Construct the message
            message = json.dumps(
                {
                    "type": "response",
                    "tasks": tasks,
                    "val_id": val_id,
                }
            )
            uri = f"ws://{ip}:{port}"
            await send_response_to_pool(uri, message, val_id)
        await asyncio.sleep(60)


async def main():
    start_server = websockets.serve(
        validator_protocol,
        base["VALIDATOR_SOCKET"]["IP"],
        base["VALIDATOR_SOCKET"]["PORT"],
    )
    await start_server
    fastapi_thread = threading.Thread(daemon=True, target=run_fastapi)
    balance_thread = threading.Thread(target=update_balance_periodically, daemon=True)
    fastapi_thread.start()
    balance_thread.start()

    periodic_task = asyncio.create_task(periodic_process_transactions())
    periodic_ping_task = asyncio.create_task(periodic_send_ping())
    periodic_info_task = asyncio.create_task(periodic_send_task_to_iNode())
    periodic_validate_task = asyncio.create_task(periodic_process_validate_task())
    periodic_pool_task = asyncio.create_task(periodic_send_task_to_pool())

    try:
        await asyncio.gather(
            periodic_task,
            periodic_ping_task,
            periodic_info_task,
            periodic_validate_task,
            periodic_pool_task,
        )
    except KeyboardInterrupt:
        logging.info("Shutting down Validator due to KeyboardInterrupt.")
    finally:
        logging.info("Validator shutdown process starting.")
        periodic_task.cancel()
        periodic_ping_task.cancel()
        periodic_info_task.cancel()
        periodic_validate_task.cancel()
        periodic_pool_task.cancel()

        await asyncio.gather(
            periodic_task,
            periodic_ping_task,
            periodic_info_task,
            periodic_validate_task,
            periodic_pool_task,
            return_exceptions=True,
        )
        logging.info("Validator shutdown process complete.")


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
        logging.info("Shutting down Validator due to KeyboardInterrupt.")

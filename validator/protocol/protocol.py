import threading
import json
import asyncio
import websockets
from datetime import datetime, timedelta, date
import time
import sys
import os
import logging
import base58
from task.task import handle_pool_response, delete_inode_task, delete_pool_task
from utils.layout import base

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

active_connections = set()
validator_connections = set()
MAX_CONCURRENT_POOLS = base["MAX_CONCURRENT"]["POOLS"]


def is_valid_address(address: str) -> bool:
    try:
        _ = bytes.fromhex(address)
        return len(address) == 128
    except ValueError:
        try:
            decoded_bytes = base58.b58decode(address)
            if len(decoded_bytes) != 33:
                return False
            specifier = decoded_bytes[0]
            if specifier not in [42, 43]:
                return False
            return True
        except ValueError:

            return False
    except Exception as e:
        print(f"Error validating address: {e}")
        return False


async def validator_protocol(websocket):
    global active_connections
    num_active_connections = len(active_connections)
    logging.info(f"active_connections {num_active_connections}")
    if len(active_connections) >= MAX_CONCURRENT_POOLS:
        await websocket.close(reason="ERROR: Max connection limit reached")
        return
    active_connections.add(websocket)
    try:
        async for message in websocket:
            try:
                parsed_message = json.loads(message)
                # print("parsed_message", parsed_message)
                message_type = parsed_message.get("type")
                pool_wallet = parsed_message.get("pool_wallet")
                val_id = parsed_message.get("val_id")
                task_info = parsed_message.get("task_info")
                pool_ip = parsed_message.get("pool_ip")
                pool_port = parsed_message.get("pool_port")

                if message_type == "validateTask":
                    success, message = await handle_pool_response(
                        val_id, task_info, pool_wallet, pool_ip, pool_port
                    )

                    data = json.dumps(
                        {
                            "type": "taskReceived",
                            "val_id": val_id,
                            "validator_wallet": base["VALIDATOR_WALLETS"][
                                "VAL_ADDRESS"
                            ],
                        }
                    )
                    if success:
                        await websocket.send(data)
                        await websocket.close()
                        active_connections.discard(websocket)
                    else:
                        await websocket.send(f"ERROR: {message}")
                        await websocket.close()
                        active_connections.discard(websocket)

                elif message_type == "PING":
                    await websocket.send("SUCCESS: Ping")
                else:
                    await websocket.send("ERROR: Unknown message type")
                    await websocket.close()
                    active_connections.discard(websocket)

            except json.JSONDecodeError:
                await websocket.send("ERROR: Invalid message format")
                await websocket.close()
                active_connections.discard(websocket)

    except websockets.ConnectionClosed:
        logging.error("Client disconnected")
        active_connections.discard(websocket)
    finally:
        await websocket.wait_closed()
        logging.info("Client disconnected")
        active_connections.discard(websocket)


async def send_response_to_pool(pool_info, message, val_id):
    uri = pool_info
    try:
        async with websockets.connect(uri) as websocket:
            logging.info(f"Successfully connected with pool: {uri}")
            await websocket.send(message)
            response = await asyncio.wait_for(websocket.recv(), timeout=60)
            await websocket.close()
            if response.startswith("SUCCESS:"):
                logging.info(f"Pool response: Accepted scores")
                output = delete_pool_task(val_id)
                logging.info(f"{output}")
            else:
                logging.error(f"Pool response: {response}")
            return
    except asyncio.TimeoutError:
        logging.error(f"Timeout when sending message to {uri}")
    except Exception as e:
        logging.error(
            f"send_response_to_pool: Error when sending message to {uri}: {e}"
        )
    return None


async def send_ping_to_iNode(uri, message):
    try:
        async with websockets.connect(uri) as websocket:
            logging.info(f"Connected for PING: {uri}")
            await websocket.send(message)
            response = await asyncio.wait_for(websocket.recv(), timeout=60)
            logging.info(f"iNode Ping response: {response}")
    except asyncio.TimeoutError:
        logging.error(f"Timeout when sending PING to {uri}")
    except Exception as e:
        logging.error(f"send_ping_to_iNode: Error when sending PING to {uri}: {e}")
    return None


async def send_task_to_iNode(uri, message, val_id):
    try:
        async with websockets.connect(uri) as websocket:
            logging.info(f"Connected for iNode task: {uri}")
            await websocket.send(message)
            response = await asyncio.wait_for(websocket.recv(), timeout=60)
            await websocket.close()
            if response.startswith("SUCCESS:"):
                # Delete the task
                output = delete_inode_task(val_id)
                logging.info(f"{output}")
            else:
                logging.info(f"iNode Task response: {response}")
            return
    except asyncio.TimeoutError:
        logging.error(f"Timeout when sending task to {uri}")
    except Exception as e:
        logging.error(f"send_task_to_iNode: Error when sending task to {uri}: {e}")
    return None

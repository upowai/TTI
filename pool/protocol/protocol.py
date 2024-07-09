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
from task.task import (
    handle_miner_response,
    is_task_valid,
    miner_eligibility,
    task_validation_output,
    find_task,
)
from database.db_requests import white_list
from utils.layout import base

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

active_connections = set()
validator_connections = set()
MAX_CONCURRENT_MINERS = base["MAX_CONCURRENT"]["MINERS"]
MAX_CONCURRENT_VALIDATORS = base["MAX_CONCURRENT"]["VALIDATORS"]


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


async def miner_protocol(websocket):
    global active_connections
    num_active_connections = len(active_connections)
    logging.info(f"active_connections {num_active_connections}")
    if len(active_connections) >= MAX_CONCURRENT_MINERS:
        await websocket.close(reason="ERROR: Max connection limit reached")
        return
    active_connections.add(websocket)
    try:
        async for message in websocket:
            try:
                parsed_message = json.loads(message)
                # print("parsed_message", parsed_message)
                message_type = parsed_message.get("type")
                wallet_address = parsed_message.get("wallet_address")
                id = parsed_message.get("id")
                output = parsed_message.get("output")

                if wallet_address is not None and not is_valid_address(wallet_address):
                    await websocket.send("ERROR: Invalid wallet address")
                    await websocket.close()
                    active_connections.discard(websocket)
                    continue

                if base["WHITE_LIST"]["ACTIVE"] == "True":
                    if wallet_address is not None and not white_list(wallet_address):
                        await websocket.send("ERROR: You are not a registered miner")
                        await websocket.close()
                        active_connections.discard(websocket)
                        continue

                if wallet_address is not None and not miner_eligibility(wallet_address):
                    await websocket.send(
                        "ERROR: You are banned from mining, too high negative score"
                    )
                    await websocket.close()
                    active_connections.discard(websocket)
                    continue

                if message_type == "request":
                    task_id, task_details = await find_task(wallet_address)
                    if task_id and task_details:
                        # print(f"Found task: {task_id} - {task_details}")
                        task_details = json.dumps(task_details)
                        await websocket.send(task_details)
                        await websocket.close()
                        active_connections.discard(websocket)
                    else:
                        await websocket.send("ERROR: No task found!")
                        await websocket.close()
                        active_connections.discard(websocket)

                elif message_type == "PING":
                    await websocket.send("SUCCESS: pong")
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


async def validation_protocol(websocket):
    global validator_connections
    num_active_connections = len(validator_connections)
    logging.info(f"validator_connections {num_active_connections}")
    if len(validator_connections) >= MAX_CONCURRENT_VALIDATORS:
        await websocket.close(reason="ERROR: Max connection limit reached")
        return
    validator_connections.add(websocket)
    try:
        async for message in websocket:
            try:
                parsed_message = json.loads(message)
                print("parsed_message: validation_protocol", parsed_message)
                message_type = parsed_message.get("type")
                validator_address = parsed_message.get("validator_address")
                val_id = parsed_message.get("val_id")
                result = parsed_message.get("tasks")

                if validator_address is not None and not is_valid_address(
                    validator_address
                ):
                    await websocket.send("ERROR: Invalid wallet address")
                    await websocket.close()
                    validator_connections.discard(websocket)
                    continue

                if val_id is not None and not is_task_valid(val_id):
                    await websocket.send("ERROR: task is invalid or expired")
                    await websocket.close()
                    validator_connections.discard(websocket)
                    continue

                if message_type == "response":
                    all_success = True
                    for entry in result:
                        wallet_address = entry.get("wallet_address")
                        tp = entry.get("tp")
                        np = entry.get("np")

                        if tp is not None:
                            success, message = task_validation_output(
                                wallet_address, tp=tp
                            )
                        elif np is not None:
                            success, message = task_validation_output(
                                wallet_address, np=np
                            )
                        else:
                            success, message = False, "Missing tp or np"

                        if not success:
                            all_success = False
                            await websocket.send(f"ERROR: {message}")
                            break

                    if all_success:
                        await websocket.send(f"SUCCESS: {val_id}")
                        await websocket.close()
                        validator_connections.discard(websocket)

                else:
                    await websocket.send("ERROR: Unknown message type")
                    await websocket.close()
                    validator_connections.discard(websocket)

            except json.JSONDecodeError:
                await websocket.send("ERROR: Invalid message format")
                await websocket.close()
                validator_connections.discard(websocket)

    except websockets.ConnectionClosed:
        logging.error("Client disconnected")
        validator_connections.discard(websocket)
    finally:
        await websocket.wait_closed()
        logging.info("Client disconnected")
        validator_connections.discard(websocket)

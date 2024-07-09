import json
import websockets
from datetime import datetime, timedelta, date
import logging
import base58
from utils.layout import base
from reward_logic.reward import find_pool, get_validator_percentage, update_scores
from reward_logic.find_validators import update_validator_info

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

active_connections = set()
validator_connections = set()
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


async def iNode_protocol(websocket):
    global active_connections
    num_active_connections = len(active_connections)
    logging.info(f"active_connections {num_active_connections}")
    if len(active_connections) >= MAX_CONCURRENT_VALIDATORS:
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
                validator_wallet = parsed_message.get("validator_wallet")
                validator_endpoint = parsed_message.get("validator_endpoint")
                val_id = parsed_message.get("val_id")
                val_ip = parsed_message.get("ip")
                val_port = parsed_message.get("port")

                if pool_wallet is not None:
                    pool_found, message = find_pool(pool_wallet)
                    if not pool_found:
                        await websocket.send(f"ERROR: {message}")
                        await websocket.close()
                        active_connections.discard(websocket)
                        continue

                if validator_wallet is not None:
                    validator_found, message = get_validator_percentage(
                        validator_wallet
                    )
                    if not validator_found:
                        await websocket.send(f"ERROR: {message}")
                        await websocket.close()
                        active_connections.discard(websocket)
                        continue
                    if validator_found < 1:
                        await websocket.send(f"ERROR: you don't have 1% stake")
                        await websocket.close()
                        active_connections.discard(websocket)
                        continue

                if message_type == "TASK":

                    set_score, message = update_scores(pool_wallet, validator_wallet)
                    if set_score:
                        await websocket.send(f"SUCCESS: {val_id}")
                        await websocket.close()
                        active_connections.discard(websocket)
                        logging.info(f"SUCCESS: {set_score}|{message}")
                    else:
                        await websocket.send(f"ERROR: {message}")
                        await websocket.close()
                        active_connections.discard(websocket)
                        logging.info(f"ERROR: {message}")

                elif message_type == "PING":
                    update, message = update_validator_info(
                        validator_wallet, val_ip, val_port, validator_endpoint
                    )
                    if update:
                        await websocket.send("SUCCESS: Pong")
                        await websocket.close()
                        active_connections.discard(websocket)
                    else:
                        await websocket.send(f"ERROR: {message}")
                        await websocket.close()
                        active_connections.discard(websocket)
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

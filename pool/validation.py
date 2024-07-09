import asyncio
import websockets
import threading
import json
import time
import logging
import utils.config as config
import requests
from datetime import datetime, timedelta
import sys
from api.api_client import test_api_connection
from protocol.protocol import validation_protocol
from database.mongodb import test_db_connection
from utils.layout import base
from task.task import select_task_for_validation, add_processed_validator
from task.send_task import upload_images_to_endpoint


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

logging.getLogger("websockets").setLevel(logging.INFO)


websockets_dict = {}


def read_peers(file_path):
    valid_peers = []
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

            for wallet_address, details in data.items():
                ip = details.get("IP")
                port = details.get("Port")
                validator_endpoint = details.get("validator_endpoint")

                if ip and port:
                    uri = f"ws://{ip}:{port}"
                    # Append a tuple of (wallet_address, uri)
                    valid_peers.append((wallet_address, uri, validator_endpoint))
                else:
                    logging.error(f"Missing IP or Port for wallet {wallet_address}")

    except json.JSONDecodeError:
        logging.error("read_peers Error decoding JSON from the file")
    except FileNotFoundError:
        logging.error(f"read_peers File not found: {file_path}")

    return valid_peers


def read_wallet(wallet_address):
    try:
        with open("peers.json", "r") as file:
            data = json.load(file)

            for address, details in data.items():
                if address == wallet_address:
                    percentage = details.get("Percentage")
                    if percentage is not None:
                        logging.info(
                            f"Wallet: {wallet_address}, Percentage: {percentage}%"
                        )
                        return percentage
                    else:
                        logging.error(f"Percentage missing for wallet {wallet_address}")
                        return None

        logging.error(f"Wallet address {wallet_address} not found.")
        return None

    except json.JSONDecodeError:
        logging.error("read_wallet Error decoding JSON from the file")
        return None
    except FileNotFoundError:
        logging.error("read_wallet File not found: peer.json")
        return None


def save_valid_peers_to_json(vals):
    current_time = datetime.utcnow()
    timer = base["TIME"]["PEERS_TIME_MIN"]
    time_ago = current_time - timedelta(minutes=timer)
    valid_peers = {}

    for wallet_address, details in vals.items():
        try:
            details_dict = json.loads(details)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON for wallet {wallet_address}: {e}")
            continue

        percentage = details_dict.get("percentage", 0)
        ping_time = details_dict.get("ping")
        validator_endpoint = details_dict.get("validator_endpoint")

        if percentage >= 1:
            if ping_time and ping_time != "0":
                try:
                    ping_datetime = datetime.fromisoformat(ping_time)
                    if ping_datetime >= time_ago:
                        valid_peers[wallet_address] = {
                            "Percentage": percentage,
                            "IP": details_dict["ip"],
                            "Port": details_dict["port"],
                            "validator_endpoint": validator_endpoint,
                        }
                    else:
                        logging.info(
                            f"Wallet {wallet_address} ping time is older than four hours. Ping time: {ping_time}"
                        )
                except ValueError:
                    logging.error(
                        f"Invalid date format for wallet {wallet_address}. Ping time: {ping_time}"
                    )
            else:
                logging.info(
                    f"Wallet {wallet_address} has no valid ping time (found: '{ping_time}')."
                )
        else:
            logging.debug(
                f"Wallet {wallet_address} has a percentage lower than 1% (found: {percentage})."
            )

    with open("peers.json", "w") as file:
        json.dump(valid_peers, file, indent=4)
        logging.info("Valid peers have been saved to peers.json.")


def fetch_validators(validators):
    try:
        response = requests.get(validators)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        logging.error(f"Http Error:", {errh})
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error:", {errt})
    except requests.exceptions.RequestException as err:
        logging.error(f"OOps: Something Else", {err})
    return []


def fetch_peer_periodically():
    interval = base["TIME"]["FETCH_PEER_SEC"]
    while True:
        vals = fetch_validators(base["INODE_INFO"]["URL"])
        logging.info(f"validators: {vals}")
        save_valid_peers_to_json(vals)
        time.sleep(interval)


async def send_response_to_validator(validator_info, message):
    uri = validator_info
    try:
        async with websockets.connect(uri) as websocket:
            logging.info(f"Now connected with validator: {uri}")
            await websocket.send(message)
            response = await asyncio.wait_for(websocket.recv(), timeout=60)
            await websocket.close()
            return response
    except asyncio.TimeoutError:
        logging.error(f"Timeout when sending message to {uri}")
    except Exception as e:
        logging.error(f"Error when sending message to {uri}: {e}")
    return None


async def connect():
    while True:
        try:
            if not test_api_connection(base["INODE_INFO"]["URL"]):
                logging.error("Failed to establish API connection. Retrying...")
                await asyncio.sleep(30)
                continue

            success, task_data = await select_task_for_validation()
            if not success:
                logging.info("No Task found for Validation. Retrying...")
                await asyncio.sleep(60)
                continue

            task = json.loads(task_data)

            peers = read_peers("peers.json")
            if not peers:
                logging.info("No peers found or error reading peers.json Retrying...")
                await asyncio.sleep(60)
                continue

            temp_peers = [
                (validator_id, validator_info, validator_endpoint)
                for validator_id, validator_info, validator_endpoint in peers
                if validator_id not in task.get("validators", [])
            ]
            processed_validators = set()

            logging.info(f"temp_peers: {temp_peers}")

            for validator_info in temp_peers[:]:
                validator_id, validator_uri, validator_endpoint = validator_info
                logging.info(
                    f"Processing validator {validator_id} with URI {validator_uri} and endpoint and {validator_endpoint}"
                )
                if validator_id in processed_validators:
                    continue

                try:
                    # Use HTTP request to upload images to the validator's endpoint
                    status, response = upload_images_to_endpoint(validator_endpoint)
                    logging.info(f"Response from validator {validator_id}: {response}")
                    response_json = response

                    if not status or response_json.get("status") == False:
                        logging.error(
                            f"Validator {validator_id} responded with error: {response_json.get('message')}"
                        )
                        continue

                    if response_json.get("status") == True:
                        val_id = response_json.get("val_id")
                        validator_wallet = response_json.get("validator_wallet")

                        update = add_processed_validator(val_id, validator_wallet)
                        if update:
                            logging.info(
                                f"Task updated successfully for validator {validator_wallet}."
                            )
                        else:
                            logging.info(
                                f"Failed to update task for validator {validator_wallet}."
                            )
                    processed_validators.add(validator_id)
                    temp_peers.remove(validator_info)

                    temp_peers = [
                        peer
                        for peer in temp_peers
                        if peer[0] not in processed_validators
                    ]

                except json.JSONDecodeError:
                    logging.error(
                        f"Failed to parse JSON response from validator {validator_id}."
                    )
                except Exception as e:
                    logging.error(
                        f"An error occurred while processing validator {validator_id}: {str(e)}"
                    )

                if not temp_peers:
                    break

            await asyncio.sleep(120)

        except Exception as e:
            logging.error(f"An unexpected error occurred in connect: {str(e)}")
            await asyncio.sleep(190)


async def main():
    balance_thread = threading.Thread(target=fetch_peer_periodically, daemon=True)
    balance_thread.start()
    start_server = websockets.serve(
        validation_protocol,
        base["POOL_VALIDATION_SOCKET"]["IP"],
        base["POOL_VALIDATION_SOCKET"]["PORT"],
    )
    await start_server

    try:
        await connect()
    finally:
        logging.info("Validation socket shutdown process starting.")


if __name__ == "__main__":
    if not test_db_connection():
        logging.error("Failed to establish MongoDB connection. Exiting...")
        sys.exit(0)
    if not test_api_connection(base["URLS"]["API_URL"]):
        logging.error("Failed to establish API connection. Exiting...")
        sys.exit(0)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down Validation socket due to KeyboardInterrupt.")

import json
import config.config as config
import websockets
import asyncio
import logging
import argparse
import os
import base58
import torch

from task.task_request import request_task
from task.send_task import upload_task
from compute.computation import (
    log_device_info,
    get_device,
    load_model_and_pipeline,
    generate_image,
    save_image,
)
from clear.clear_task import clear_directory
import warnings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

# Suppress specific warnings
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module="transformers.models.clip.feature_extraction_clip",
)


def parse_args():
    parser = argparse.ArgumentParser(description="Miner Configuration")
    parser.add_argument(
        "--MINER_POOL_IP", required=True, help="IP address of the miner pool"
    )
    parser.add_argument(
        "--MINER_POOL_PORT", required=True, type=int, help="Port of the miner pool"
    )
    parser.add_argument(
        "--WALLET_ADDRESS", required=True, help="Wallet address for the miner"
    )
    parser.add_argument("--ENDPOINT", required=True, help="Pool endpoint")
    parser.add_argument("--DEVICE", required=True, help="Device number")
    return parser.parse_args()


def ensure_directory_exists(directory_path):
    """Ensure that a directory exists; if it doesn't, create it."""
    if not os.path.exists(directory_path):
        logging.info(f"creating {directory_path}")
        os.makedirs(directory_path)


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


async def start_miner(pipe, device_name):
    uri = f"ws://{config.MINER_POOL_IP}:{config.MINER_POOL_PORT}"
    logging.info(f"Connecting to miner pool at {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            # Send a ping message
            message = {"type": "PING"}
            await websocket.send(json.dumps(message))

            # Wait for a response
            response = await websocket.recv()
            if response.startswith("SUCCESS") or response.startswith("ERROR"):
                logging.info("Pool response: %s", response)

            # Request a task
            logging.info("Requesting a task from pool")
            request_response = await request_task(websocket, "request")
            logging.info(f"Request response: {request_response}")
            if request_response.startswith("SUCCESS") or request_response.startswith(
                "ERROR"
            ):
                logging.info("Pool response for Task: %s", request_response)

            try:
                response_data = json.loads(request_response)

                # Handle double encoded JSON if necessary
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)

                if (
                    isinstance(response_data, dict)
                    and response_data.get("message_type") == "requestedTask"
                ):
                    task_id = response_data.get("id")
                    prompt = response_data.get("task")
                    negative_prompt = response_data.get("negative_prompt")
                    seed = response_data.get("seed")
                    width = response_data.get("width")
                    height = response_data.get("height")

                    image = generate_image(
                        pipe, prompt, negative_prompt, seed, width, height, device_name
                    )
                    if image:
                        path, name = save_image(image, config.DEVICE)
                        metadata = {
                            "task_id": task_id,
                            "wallet_address": config.WALLET_ADDRESS,
                        }

                        logging.info("Sending completed task to pool")
                        result = upload_task(
                            path, f"{config.ENDPOINT}/task_upload", metadata
                        )
                        logging.info(f"Pool response: {result}")
                        if result:
                            clear_directory(path)
                            logging.info("Cleaning uploaded task")
                        else:
                            logging.error("Error: Failed to upload task")
                    else:
                        logging.error("Error: Failed to generate image")

                else:
                    logging.error("Error: Response data is not a valid JSON object.")
            except json.JSONDecodeError:
                logging.error("Error: Could not decode JSON response.")
            except TypeError:
                logging.error("TypeError: The response is not in the expected format.")
            except AttributeError:
                logging.error("AttributeError: Unexpected data type.")
    except websockets.ConnectionClosedError:
        logging.error(
            "ConnectionClosedError: The websocket connection is closed unexpectedly."
        )
    except websockets.WebSocketException as e:
        logging.error(
            "WebSocketException: An error occurred with the websocket connection. Details: %s",
            e,
        )
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)


async def start_server():
    logging.info("Starting Miner...")
    try:
        device_number = int(config.DEVICE)
        device_name = get_device(device_number)

        model_path = "amajicmixRealistic_v7"
        pipe = load_model_and_pipeline(model_path, torch.float16, device_name)
        if pipe is not None:
            while True:
                try:
                    await start_miner(pipe, device_name)
                except Exception as e:
                    logging.error("Miner closed due to an error: %s", e, exc_info=True)
                    break
                await asyncio.sleep(config.INTERVAL)
        else:
            logging.error(f"Miner closed due to an error: ")
            return
    except KeyboardInterrupt:
        logging.info("Miner shutdown initiated by user.")
    finally:
        logging.info("Shutting down Miner...")


try:
    log_device_info()

    args = parse_args()

    if not is_valid_address(args.WALLET_ADDRESS):
        logging.error(
            "Invalid wallet address provided. Please provide a valid address."
        )
        raise ValueError(
            "Invalid wallet address provided. Please provide a valid address."
        )
    else:
        # Override config values with command-line arguments
        config.MINER_POOL_IP = args.MINER_POOL_IP
        config.MINER_POOL_PORT = args.MINER_POOL_PORT
        config.WALLET_ADDRESS = args.WALLET_ADDRESS
        config.ENDPOINT = args.ENDPOINT
        config.DEVICE = args.DEVICE
        asyncio.get_event_loop().run_until_complete(start_server())
except KeyboardInterrupt:
    logging.info("Miner shutdown process complete.")

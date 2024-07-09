import json
import config.config as config
import logging
import websockets

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


async def request_task(websocket, message_type):
    try:
        message = {
            "type": message_type,
            "wallet_address": config.WALLET_ADDRESS,
        }
        await websocket.send(json.dumps(message))

        response = await websocket.recv()
        return response

    except websockets.ConnectionClosedError as e:
        logging.error("Websocket connection closed unexpectedly: %s", e)
    except websockets.WebSocketException as e:
        logging.error("Websocket error: %s", e)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
    return None

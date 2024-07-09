import json
import config.config as config
import logging
import websockets
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def upload_task(image_path, endpoint_url, metadata):
    try:
        with open(image_path, "rb") as image_file:
            files = {"file": image_file}
            response = requests.post(endpoint_url, files=files, data=metadata)

            response.raise_for_status()

            response_data = response.json()
            task_status = response_data.get("status", None)

            if task_status == "success":
                return {
                    "status": "success",
                    "message": response_data.get("data", ["Unknown message"])[1],
                }
            else:
                return {
                    "status": "error",
                    "message": response_data.get("data", ["Unknown error"])[1],
                }
    except requests.exceptions.RequestException as e:
        try:
            response_data = e.response.json()
            message = response_data.get("detail", str(e))
        except ValueError:
            message = str(e)
        return {"status": "error", "message": message}
    except FileNotFoundError:
        return {"status": "error", "message": "The specified image file was not found."}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}

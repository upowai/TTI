import os
import logging
import requests
import subprocess
import sys

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

MODEL_URL = "https://civitai.com/api/download/models/176425"
MODEL_FILE = "majicmixRealistic_v7.safetensors"
CONVERT_SCRIPT = "utils/convert.py"
DUMP_PATH = "amajicmixRealistic_v7/"


def download_model(url, filename):
    try:
        logging.info(f"Downloading model from {url} to {filename}")
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        with open(filename, "wb") as f:
            f.write(response.content)
        logging.info("Download completed successfully")
    except requests.RequestException as e:
        logging.error(f"Failed to download model: {e}")
        sys.exit(1)


def convert_model():
    try:
        logging.info(f"Converting model using {CONVERT_SCRIPT}")
        subprocess.run(
            [
                sys.executable,
                CONVERT_SCRIPT,
                "--checkpoint_path",
                MODEL_FILE,
                "--dump_path",
                DUMP_PATH,
                "--from_safetensors",
            ],
            check=True,
        )
        logging.info("Model conversion completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Model conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if not os.path.exists(MODEL_FILE):
        download_model(MODEL_URL, MODEL_FILE)
    else:
        logging.info("Model file already exists. Skipping download.")

    convert_model()

import requests
import hashlib
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

API_URL = "https://pooltti.upow.network"


def get_challenge():
    response = requests.get(f"{API_URL}/generate_challenge/")
    logger.info("Challenge received from the server")
    return response.json()


def mine(challenge, wallet_address):
    difficulty = challenge["difficulty"]
    logger.info(f"Starting mining with difficulty: {difficulty}")
    index = challenge["index"]
    target = "0" * difficulty + "f" * (64 - difficulty)
    nonce = 0

    start_time = time.time()
    last_log_time = start_time
    hashes_processed = 0

    while True:
        text = f"{challenge['time']}:{challenge['previous_hash']}:{wallet_address}:{nonce}:{index}"
        hash_result = hashlib.sha256(text.encode()).hexdigest()
        hashes_processed += 1
        if hash_result < target:
            elapsed_time = time.time() - start_time
            logger.info(f"Mining completed in {elapsed_time:.2f} seconds")
            logger.info(f"Nonce: {nonce}, Hash: {hash_result}")
            return nonce, hash_result
        nonce += 1
        current_time = time.time()
        if current_time - last_log_time >= 5:
            hashes_per_second = hashes_processed / (current_time - start_time)
            logger.info(
                f"Processed {hashes_processed / 1_000_000:.2f} million hashes so far (Rate: {hashes_per_second / 1_000_000:.2f} million hashes/second)"
            )
            last_log_time = current_time


def submit_result(challenge, nonce, result_hash, wallet_address):
    payload = {
        "index": challenge["index"],
        "nonce": nonce,
        "result_hash": result_hash,
        "wallet_address": wallet_address,
        "time": challenge["time"],
        "previous_hash": challenge["previous_hash"],
        "difficulty": challenge["difficulty"],
        "target": challenge["target"],
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{API_URL}/submit_result/", json=payload, headers=headers)
    logger.info("Result submitted to the server")

    return response.json()


if __name__ == "__main__":
    try:
        challenge = get_challenge()
        wallet_address = "wallet201"
        logger.info(f"Challenge details: {challenge}")
        nonce, result_hash = mine(challenge, wallet_address)
        result = submit_result(challenge, nonce, result_hash, wallet_address)
        logger.info(f"Submission result: {result}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

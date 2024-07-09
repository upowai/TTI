import requests
import hashlib

API_URL = "http://0.0.0.0:8003"


def get_challenge():
    response = requests.get(f"{API_URL}/generate_challenge/")
    print("response", response)
    return response.json()


def mine(challenge, wallet_address):
    difficulty = challenge["difficulty"]
    print("difficulty_mine", difficulty)
    index = challenge["index"]
    target = "0" * difficulty + "f" * (64 - difficulty)
    nonce = 0
    while True:
        text = f"{challenge['time']}:{challenge['previous_hash']}:{wallet_address}:{nonce}:{index}"
        hash_result = hashlib.sha256(text.encode()).hexdigest()
        if hash_result < target:
            return nonce, hash_result
        nonce += 1


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

    return response.json()


# Example usage
challenge = get_challenge()
wallet_address = "wallet201"
print("challenge", challenge)
nonce, result_hash = mine(challenge, wallet_address)
print("mining compeleted")
result = submit_result(challenge, nonce, result_hash, wallet_address)
print(result)

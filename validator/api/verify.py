import hashlib
import upowpy as upow
import json
from fastecdsa import ecdsa, curve
from datetime import datetime
import logging
from utils.layout import base

from protocol.protocol import is_valid_address
from api.api_client import fetch_pools

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def verify_signature(signature, pool_address, hash_str):
    try:
        if not is_valid_address(pool_address):
            logging.info(f"Invalid pool wallet address")
            return False, "Invalid pool wallet address"

        # Split the signature string into r and s
        r, s = map(int, signature.split(","))

        public_key = upow.address_to_publickey(pool_address)

        # Verify the signature
        valid = ecdsa.verify((r, s), hash_str, public_key, curve=curve.P256)

        if valid == True:
            logging.info(f"Signature verification successful")
            return True, "Signature verification successful"
        else:
            logging.info(f"Signature verification failed")
            return False, "Signature verification failed"
    except Exception as e:
        return False, f"An error occurred in verify_signature: {str(e)}"


def hash_data_for_comparison(validation_task):
    data_for_hash = {
        "val_id": validation_task.val_id,
        "pool_ip": validation_task.pool_ip,
        "pool_port": validation_task.pool_port,
        "pool_wallet": validation_task.pool_wallet,
        "condition": validation_task.condition,
        "createdAt": (
            validation_task.createdAt.isoformat()
            if isinstance(validation_task.createdAt, datetime)
            else validation_task.createdAt
        ),
        "tasks": [],
    }

    for task in validation_task.tasks:
        task_data = {
            "id": task.id,
            "retrieve_id": task.retrieve_id,
            "task": task.task,
            "negative_prompt": task.negative_prompt,
            "wallet_address": task.wallet_address,
            "width": task.width,
            "height": task.height,
            "seed": task.seed,
            "time": task.time,
            "status": task.status,
            "type": task.type,
            "message_type": task.message_type,
        }
        data_for_hash["tasks"].append(task_data)

    return hash_data(data_for_hash)


def hash_data(data):
    json_data = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(json_data).hexdigest()


def validate_pool_address(pool_address):
    pools_url = base["INODE_INFO"]["POOL_URL"]
    pools = fetch_pools(pools_url)

    print("pools", pools)
    print("pool_address", pool_address)

    if pools is None:
        return False, "No pools have been registered yet"

    if pool_address in pools:
        return True, "Found registered pool"
    else:
        return False, "Pool not registered"

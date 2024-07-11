from fastapi import FastAPI, HTTPException, Query, Request, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
import os
import json
import logging
import base64
from dotenv import load_dotenv


from database.db_requests import add_pool, remove_pool, get_pools_list
from database.db_requests import get_validators_list

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

dotenv_path = ".env"
load_dotenv(dotenv_path)

b64_private_key = os.getenv("SHA_PRIVATE_KEY")
if b64_private_key is None:
    print(
        "SHA_PRIVATE_KEY not found. Please run 'python generatekey.py' to set the key in the .env variable."
    )
    exit(0)

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    pem_private_key = base64.b64decode(b64_private_key)
    private_key = serialization.load_pem_private_key(
        pem_private_key,
        password=None,
    )
except Exception as e:
    logging.error(f"Error loading private key: {e}")
    raise


def decrypt_message(private_key, encrypted_message):
    try:
        return private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except InvalidSignature:
        raise ValueError("Invalid signature")
    except Exception as e:
        logging.error(f"Error in decryption: {e}")
        raise ValueError("Decryption failed")


@app.post("/modify-pool-list/")
async def modify_pool_list(request: Request):
    try:
        body = await request.body()
        decrypted_message = decrypt_message(private_key, body)
        action, publickey_value = decrypted_message.decode().split(":")

        if action == "add":
            return add_pool(publickey_value)
        elif action == "remove":
            return remove_pool(publickey_value)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
    except ValueError as e:
        logging.error(f"Value error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"modify_pool_list Unexpected error: {e}")
        # Handle unexpected errors gracefully
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/validators")
def get_validators():
    try:
        result = get_validators_list()
        if not result:
            raise HTTPException(status_code=400, detail="No validators found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/pools")
def get_pools():
    try:
        result = get_pools_list()
        if not result:
            raise HTTPException(status_code=400, detail="No pools found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

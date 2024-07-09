from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi import File, Form, UploadFile
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import hashlib
from pydantic import BaseModel
import asyncio

from database.mongodb import (
    miners,
    challenges,
)
from database.db_requests import (
    check_active_users,
    get_balance_from_wallet,
    get_balance_poolowner,
    deduct_balance_from_wallet,
    deduct_balance_from_poolowner,
)
from utils.layout import base

from task.task import handle_miner_response

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


class ResultSubmission(BaseModel):
    nonce: int
    challenge_id: str
    result_hash: str
    wallet_address: str


class Challenge(BaseModel):
    time: str
    previous_hash: str
    difficulty: int
    target: str


class DeductBalanceRequest(BaseModel):
    wallet_address: str
    amount_to_deduct: float


class DeductBalancePool(BaseModel):
    amount_to_deduct: float


class SubmitData(BaseModel):
    index: int
    nonce: int
    result_hash: str
    wallet_address: str
    time: str
    previous_hash: str
    difficulty: int
    target: str


def generate_target(difficulty):
    return "0" * difficulty + "f" * (64 - difficulty)


async def register_miner(wallet_address, difficulty, hash, index):
    try:
        # Check if the miner is already registered
        existing_miner = miners.find_one({"wallet_address": wallet_address})
        if existing_miner:
            print("Miner with this wallet address is already registered.")
            return False, "Miner with this wallet address is already registered."

        # Check total number of miners
        miner_count = miners.count_documents({})
        if miner_count >= base["WHITE_LIST"]["MAX_MINERS"]:
            print("MAX MINERS REACHED")

            # Find the oldest miner
            oldest_miner_cursor = (
                miners.find().sort([("difficulty", 1), ("time_registered", 1)]).limit(1)
            )
            oldest_miner = list(oldest_miner_cursor)

            # Calculate time difference to check against immunity period
            time_diff = datetime.utcnow() - oldest_miner[0]["time_registered"]
            print("oldest_miner", oldest_miner)
            print(
                f'DIFFERENCE: {time_diff} : {datetime.utcnow()} - {oldest_miner[0]["time_registered"]}'
            )
            print(f' IMMUNITY: {base["WHITE_LIST"]["IMMUNITY"]}')

            if time_diff.total_seconds() > base["WHITE_LIST"]["IMMUNITY"]:
                print("removing someone")
                old_wallet_address = oldest_miner[0]["wallet_address"]
                print(f"{old_wallet_address} replaced by new {wallet_address}")
                miners.delete_one({"_id": oldest_miner[0]["_id"]})
            else:
                print("No miner spot available due to immunity period.")
                return False, "No miner spot available due to immunity period."

        # Register the new miner if a spot is available
        miner_data = {
            "wallet_address": wallet_address,
            "hash": hash,
            "time_registered": datetime.utcnow(),
            "difficulty": difficulty,
            "miner_id": (
                miner_count + 1
                if miner_count < base["WHITE_LIST"]["MAX_MINERS"]
                else oldest_miner[0]["miner_id"]
            ),
            "index": index,
        }
        miners.insert_one(miner_data)
        print("Miner registered successfully")
        return True, None
    except Exception as e:
        # Return error details if an exception occurs
        print(f"An error occurred during the registration process: {str(e)}")
        return False, f"An error occurred during the registration process: {str(e)}"


@app.get("/generate_challenge/")
@limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT1"])
async def generate_challenge(request: Request):
    try:
        miner_count = miners.count_documents({})
        challenge_count = challenges.count_documents({})
        print("miner_count", miner_count)
        print("challenge_count", challenge_count)

        index = challenge_count + 1

        if challenge_count == 0:
            print("came to situation where NO genesis challenge exist")
            difficulty = base["WHITE_LIST"]["DEFAULT_DIFFICULTY"]
            print("difficulty", difficulty)
            previous_hash = "0" * 64
            genesis_target = generate_target(difficulty)
            challenge = {
                "index": index,
                "difficulty": difficulty,
                "time": datetime.utcnow(),
                "previous_hash": previous_hash,
                "number_of_miners": miner_count,
                "target": genesis_target,
            }
            print("genesis_challenge", challenge)
            return challenge
        else:
            print("came to situation where genesis challenge exist")
            # Calculate difficulty but ensure it doesn't go below default difficulty
            adjusted_difficulty = base["WHITE_LIST"]["DEFAULT_DIFFICULTY"] + (
                (miner_count - base["WHITE_LIST"]["BASE_MINER_COUNT"])
                // base["WHITE_LIST"]["INCREASE_DIFFICULTY"]
            )
            difficulty = max(
                base["WHITE_LIST"]["DEFAULT_DIFFICULTY"], adjusted_difficulty
            )
            print("adjusted difficulty", difficulty)

            last_challenge = challenges.find_one(sort=[("_id", -1)])
            if last_challenge is None:
                previous_hash = "0" * 64
            else:
                previous_hash = last_challenge["result_hash"]

            target = generate_target(difficulty)
            challenge = {
                "index": index,
                "difficulty": difficulty,
                "time": datetime.utcnow(),
                "previous_hash": previous_hash,
                "number_of_miners": miner_count,
                "target": target,
            }

            return challenge  # Return but do not save
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit_result/")
async def submit_result(
    request: Request,
    submit_request: SubmitData,
):
    try:
        index = submit_request.index
        nonce = submit_request.nonce
        result_hash = submit_request.result_hash
        wallet_address = submit_request.wallet_address
        time = submit_request.time
        previous_hash = submit_request.previous_hash
        difficulty = submit_request.difficulty
        target = submit_request.target

        text = f"{time}:{previous_hash}:{wallet_address}:{nonce}:{index}"

        computed_hash = hashlib.sha256(text.encode()).hexdigest()

        if computed_hash != result_hash:
            raise HTTPException(
                status_code=400, detail="Hash does not match the computed result"
            )

        if result_hash >= target:
            raise HTTPException(
                status_code=400, detail="Result does not meet the challenge target"
            )

        registered_miner = miners.find_one({"wallet_address": wallet_address})
        if registered_miner:
            raise HTTPException(
                status_code=400,
                detail="Miner with this wallet address is already registered and cannot submit new results",
            )

        existing_document = challenges.find_one({"index": index})
        if existing_document:
            raise HTTPException(
                status_code=400,
                detail="A valid result for this challenge has already been submitted",
            )

        data = {
            "index": index,
            "nonce": nonce,
            "result_hash": result_hash,
            "wallet_address": wallet_address,
            "time": time,
            "previous_hash": previous_hash,
            "difficulty": difficulty,
            "target": target,
        }

        registration_success, registration_message = await register_miner(
            wallet_address, difficulty, result_hash, index
        )
        if not registration_success:
            raise HTTPException(status_code=409, detail=registration_message)

        result = challenges.insert_one(data)
        if result.inserted_id:
            return {
                "message": "Result accepted",
                "challenge_id": str(result.inserted_id),
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to insert the challenge result",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/active-miners")
@limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT1"])
def get_active_users(request: Request):
    try:
        return {"active_miners": check_active_users()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_balance/")
@limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT1"])
async def get_balance(request: Request, wallet_address: str):
    if not wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address must be provided")

    balance = get_balance_from_wallet(wallet_address)
    if isinstance(balance, str) and balance.startswith("Error"):

        raise HTTPException(
            status_code=404 if "not found" in balance else 400, detail=balance
        )

    return {"balance": balance}


@app.get("/get_balance_poolowner/")
@limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT1"])
async def poolowner_get_balance(request: Request):
    balance = get_balance_poolowner()
    if isinstance(balance, str) and balance.startswith("Error"):

        raise HTTPException(
            status_code=404 if "not found" in balance else 400, detail=balance
        )
    return {"balance": balance}


@app.post("/deduct_balance/")
@limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT2"])
async def deduct_balance(
    request: Request,
    deduct_request: DeductBalanceRequest,
):
    result, response = deduct_balance_from_wallet(
        deduct_request.wallet_address, deduct_request.amount_to_deduct
    )
    if result is None:
        raise HTTPException(status_code=400, detail=response)

    return {"message": f"Amount deducted successfully: {response}"}


@app.post("/poolowner_deduct_balance/")
@limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT1"])
async def poolowner_deduct_balance(
    request: Request,
    deduct_request: DeductBalancePool,
):
    result, response = deduct_balance_from_poolowner(deduct_request.amount_to_deduct)
    if result is None:
        raise HTTPException(status_code=400, detail=response)

    return {"message": f"Amount deducted successfully: {response}"}


# @app.get("/latestwithdraws/")
# @limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT1"])
# async def latest_withdraws(request: Request, wallet_address: str):
#     if not wallet_address:
#         raise HTTPException(status_code=400, detail="Wallet address must be provided")

#     result = get_miner_TransactionsPushed(wallet_address)

#     if not result.get("success", False):
#         message = result.get("message", "An unexpected error occurred")
#         status_code = 404 if "No details found" in message else 500
#         raise HTTPException(status_code=status_code, detail=message)
#     return result.get("data", {})


@app.post("/task_upload")
async def upload_image(
    task_id: str = Form(...),
    wallet_address: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        image_bytes = await file.read()
        # Check if the file size exceeds 3 MB (3 * 1024 * 1024 bytes)
        if len(image_bytes) > 3 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 3 MB",
            )
        await asyncio.sleep(20)

        response = await handle_miner_response(task_id, wallet_address, image_bytes)
        return JSONResponse(content={"status": "success", "data": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

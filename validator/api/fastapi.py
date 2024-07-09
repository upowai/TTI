from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

from database.db_requests import (
    get_balance_from_wallet,
    get_balance_entityOwners,
    deduct_balance_from_wallet,
    deduct_balance_from_entityOwners,
)
from task.task import handle_pool_response
from utils.layout import base
from api.verify import verify_signature, hash_data_for_comparison, validate_pool_address


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


class Task(BaseModel):
    id: Optional[str]
    retrieve_id: Optional[str]
    task: Optional[str]
    negative_prompt: Optional[str]
    wallet_address: Optional[str]
    width: Optional[int]
    height: Optional[int]
    seed: Optional[str]
    time: Optional[str]
    status: Optional[str]
    type: Optional[str]
    message_type: Optional[str]
    output: Optional[str]  # base64 encoded image data


class ValidationTask(BaseModel):
    val_id: Optional[str]
    pool_ip: Optional[str]
    pool_port: Optional[str]
    pool_wallet: Optional[str]
    condition: Optional[str]
    createdAt: Optional[datetime]
    tasks: List[Task]
    signature: Optional[str]
    hash_str: Optional[str]


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


@app.get("/get_balance_entityOwners/")
@limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT1"])
async def poolowner_get_balance(request: Request):
    balance = get_balance_entityOwners()
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


@app.post("/entityOwners_deduct_balance/")
@limiter.limit(base["RATE_LIMIT"]["RATE_LIMIT1"])
async def valowner_deduct_balance(
    request: Request,
    deduct_request: DeductBalancePool,
):
    result, response = deduct_balance_from_entityOwners(deduct_request.amount_to_deduct)
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


@app.post("/upload_tasks/")
async def upload_tasks(validation_task: ValidationTask):
    try:

        pool, result = validate_pool_address(validation_task.pool_wallet)
        if not pool:
            raise HTTPException(
                status_code=400,
                detail=result,
            )

        computed_hash_str = hash_data_for_comparison(validation_task)
        if computed_hash_str != validation_task.hash_str:
            raise HTTPException(
                status_code=400,
                detail="Data hash mismatch, possible tampering detected",
            )

        success, message = verify_signature(
            validation_task.signature,
            validation_task.pool_wallet,
            validation_task.hash_str,
        )
        if not success:
            raise HTTPException(
                status_code=400,
                detail=message,
            )

        # Convert Task objects to dictionaries
        task_info = [task.model_dump() for task in validation_task.tasks]

        result, info = await handle_pool_response(
            val_id=validation_task.val_id,
            task_info=task_info,
            pool_wallet=validation_task.pool_wallet,
            pool_ip=validation_task.pool_ip,
            pool_port=validation_task.pool_port,
        )
        logging.info(f"{info}")

        validator_address = base["VALIDATOR_WALLETS"]["VAL_ADDRESS"]

        if not result:
            return JSONResponse(content={"status": result, "message": info})
        else:
            return JSONResponse(
                content={
                    "status": result,
                    "message": "Successfully received all tasks",
                    "val_id": validation_task.val_id,
                    "validator_wallet": validator_address,
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

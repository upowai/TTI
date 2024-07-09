#iNode Documentation

## (`main.py`) Documentation

The `iNode` script orchestrates several tasks essential for maintaining a blockchain reward system. It utilizes FastAPI for API endpoints, connects to a MongoDB database, and processes transactions and rewards through periodic tasks.

## Key Components

### 1. Logging Configuration

```python
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)
```

**Purpose**: Sets up logging to provide timestamps and log levels for debugging and monitoring.

### 2. Function: `run_fastapi`

```python
def run_fastapi():
    uvicorn.run(
        app,
        host=base["FAST_API"]["FAST_API_URL"],
        port=base["FAST_API"]["FAST_API_PORT"],
    )
```

**Purpose**: Starts the FastAPI server using settings from the configuration file.

### 3. Function: `periodic_process_transactions`

```python
async def periodic_process_transactions():
    try:
        while True:
            process_block_rewards()
            await asyncio.sleep(base["TIME"]["CHECK_INTERVAL"])
    except Exception as e:
        print(f"Error in periodic_process_transactions: {e}")
```

**Purpose**: Periodically processes block rewards at specified intervals.

### 4. Function: `update_balance_periodically`

```python
def update_balance_periodically():
    try:
        while True:
            # process_all_transactions()
            time.sleep(base["TIME"]["PUSH_TX"])
    except Exception as e:
        print(f"Error in update_balance_periodically: {e}")
```

**Purpose**: Placeholder function to update balances periodically. (Note: `process_all_transactions` is commented out.)

### 5. Function: `update_validators_periodically`

```python
def update_validators_periodically():
    try:
        while True:
            update_validators_list()
            time.sleep(base["TIME"]["FETCH_VALIDATORS"])
    except Exception as e:
        print(f"Error in update_validators_periodically: {e}")
```

**Purpose**: Periodically updates the list of validators at specified intervals.

### 6. Function: `decay_scores_periodically`

```python
def decay_scores_periodically():
    try:
        while True:
            decay_pool_score()
            decay_validator_score()
            time.sleep(base["TIME"]["DECAY"])
    except Exception as e:
        print(f"Error in decay_scores_periodically: {e}")
```

**Purpose**: Periodically decays pool and validator scores.

### 7. Function: `main`

```python
async def main():
    start_server = websockets.serve(
        iNode_protocol,
        base["INODE_MAIN_SOCKET"]["IP"],
        base["INODE_MAIN_SOCKET"]["PORT"],
    )
    await start_server
    fastapi_thread = threading.Thread(daemon=True, target=run_fastapi)
    balance_thread = threading.Thread(target=update_balance_periodically, daemon=True)
    fetch_val_thread = threading.Thread(
        target=update_validators_periodically, daemon=True
    )
    scores_thread = threading.Thread(target=decay_scores_periodically, daemon=True)
    fastapi_thread.start()
    fetch_val_thread.start()
    balance_thread.start()
    scores_thread.start()

    periodic_task = asyncio.create_task(periodic_process_transactions())

    try:
        await asyncio.gather(periodic_task)
    except KeyboardInterrupt:
        logging.info("Shutting down iNode due to KeyboardInterrupt.")
    finally:
        logging.info("iNode shutdown process starting.")
        periodic_task.cancel()

        await asyncio.gather(
            periodic_task,
            return_exceptions=True,
        )
        logging.info("iNode shutdown process complete.")
```

**Purpose**:

- Starts the WebSocket server.
- Initiates threads for running FastAPI, updating balances, validators, and decaying scores.
- Manages the main asynchronous task for processing transactions.
- Handles graceful shutdown on keyboard interrupt.

### 8. Main Execution Block

```python
if __name__ == "__main__":
    if not test_db_connection():
        logging.error("Failed to establish MongoDB connection. Exiting...")
        sys.exit(1)
    if not test_api_connection(base["URLS"]["API_URL"]):
        logging.error("Failed to establish API connection. Exiting...")
        sys.exit(2)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down iNode due to KeyboardInterrupt.")
```

**Purpose**:

- Tests database and API connections before starting the main process.
- Runs the main function asynchronously.
- Ensures a clean shutdown on keyboard interrupt.

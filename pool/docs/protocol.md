# (`protocol.py`) Documentation

## `miner_protocol`

Handles WebSocket connections for miners. It validates wallet addresses, checks if miners are whitelisted, verifies miner eligibility, and processes task requests and responses.

**Process:**

1. **Connection Management:**
   - Limits the number of active connections based on `MAX_CONCURRENT_MINERS`.
   - Closes the connection if the limit is reached.
2. **Message Handling:**
   - Parses incoming messages and extracts message type, wallet address, and other relevant data.
   - Validates wallet addresses using `is_valid_address`.
   - Checks if the miner is whitelisted using `white_list`.
   - Verifies miner eligibility using `miner_eligibility`.
3. **Task Handling:**
   - Processes task responses and requests using `handle_miner_response` and `find_task`.
4. **Ping Handling:**
   - Responds to PING messages with "pong".
5. **Error Handling:**
   - Sends error messages for invalid formats, unknown message types, or if the wallet is invalid, not whitelisted, or ineligible.

**Returns:**

- Manages WebSocket connections, sending responses or closing connections based on message validity.

**Example Usage:**

```python
# Within an asyncio event loop
await miner_protocol(websocket)
```

---

#### Usage:

- **Start a WebSocket Server**: The `miner_protocol` should be invoked by a WebSocket server to handle incoming connections from miners.

#### Inputs:

- **WebSocket Messages**: JSON formatted messages containing the following keys:
  - `type`: `"response"`, `"request"`, or `"PING"`
  - `wallet_address`: The miner's wallet address (optional)
  - `id`: Task ID for responses (optional)
  - `output`: Task output for responses (optional)

#### Outputs:

- **WebSocket Responses**: JSON formatted messages sent back to the client:
  - For invalid wallet addresses: `"ERROR: Invalid wallet address"`
  - For non-whitelisted wallets: `"ERROR: You are not a registered miner"`
  - For ineligible miners: `"ERROR: You are banned from mining, too high negative score"`
  - For task responses: `"SUCCESS: Task accepted"` or `"ERROR: [message]"`
  - For task requests: Task details in JSON format or `"ERROR: No task found!"`
  - For pings: `"SUCCESS: pong"`
  - For unknown message types: `"ERROR: Unknown message type"`
  - For invalid message formats: `"ERROR: Invalid message format"`
  - For max connection limit: WebSocket connection closed with reason `"ERROR: Max connection limit reached"`

### `validation_protocol`

**Purpose:** Handle communication protocol for validators.

**Process:**

1. **Connection Management:**
   - Limits the number of active connections based on `MAX_CONCURRENT_VALIDATORS`.
   - Closes the connection if the limit is reached.
2. **Message Handling:**
   - Parses incoming messages and extracts message type, validator address, and other relevant data.
   - Validates wallet addresses using `is_valid_address`.
   - Checks task validity using `is_task_valid`.
3. **Task Validation:**
   - Processes task validation responses using `task_validation_output`.
4. **Error Handling:**
   - Sends error messages for invalid formats, unknown message types, or if the wallet is invalid or the task is not valid.

**Returns:**

- Manages WebSocket connections, sending responses or closing connections based on message validity.

**Example Usage:**

```python
# Within an asyncio event loop
await validation_protocol(websocket)
```

---

#### Usage:

- **Start a WebSocket Server**: The `validation_protocol` should be invoked by a WebSocket server to handle incoming connections from validators.

#### Inputs:

- **WebSocket Messages**: JSON formatted messages containing the following keys:
  - `type`: `"response"`
  - `validator_address`: The validator's wallet address
  - `val_id`: Validation task ID
  - `tasks`: List of task results, each with:
    - `wallet_address`: The miner's wallet address
    - `tp`: True positive count (optional)
    - `np`: Negative point count (optional)

#### Outputs:

- **WebSocket Responses**: JSON formatted messages sent back to the client:
  - For invalid wallet addresses: `"ERROR: Invalid wallet address"`
  - For invalid or expired tasks: `"ERROR: task is invalid or expired"`
  - For task validation results: `"SUCCESS: [val_id]"` or `"ERROR: [message]"`
  - For unknown message types: `"ERROR: Unknown message type"`
  - For invalid message formats: `"ERROR: Invalid message format"`
  - For max connection limit: WebSocket connection closed with reason `"ERROR: Max connection limit reached"`

### `is_valid_address`

**Process:**

1. **Hexadecimal Check:** Attempts to decode the address from hexadecimal.
   - Valid if the address length is 128.
2. **Base58 Check:** If the hexadecimal check fails, attempts Base58 decoding.
   - Valid if decoded bytes length is 33 and the first byte (specifier) is 42 or 43.
3. **Error Handling:** Returns `False` if any exception occurs.

**Returns:**

- `True` if the address is valid.
- `False` if the address is invalid.

**Example Usage:**

```python
is_valid_address("E3sGYEhVznzmjFGv99bhqWQrRoKsbRUuRwYJRHEUtxneu")
# Result: True
```

---

### `white_list`

**Purpose:** Check if a wallet address is whitelisted.

**Process:**

1. **Check Wallet:** Verifies if the wallet is in the predefined list of whitelisted wallets.
2. **Error Handling:** Returns `False` if any exception occurs.

**Returns:**

- `True` if the wallet is whitelisted.
- `False` if the wallet is not whitelisted.

**Example Usage:**

```python
white_list("E3sGYEhVznzmjFGv99bhqWQrRoKsbRUuRwYJRHEUtxneu")
# Result: True
```

---

### `validation_protocol`

**Purpose:** Handle communication protocol for validators.

**Process:**

1. **Connection Management:**
   - Limits the number of active connections based on `MAX_CONCURRENT_VALIDATORS`.
   - Closes the connection if the limit is reached.
2. **Message Handling:**
   - Parses incoming messages and extracts message type, validator address, and other relevant data.
   - Validates wallet addresses using `is_valid_address`.
   - Checks task validity using `is_task_valid`.
3. **Task Validation:**
   - Processes task validation responses using `task_validation_output`.
4. **Error Handling:**
   - Sends error messages for invalid formats, unknown message types, or if the wallet is invalid or the task is not valid.

**Returns:**

- Manages WebSocket connections, sending responses or closing connections based on message validity.

**Example Usage:**

```python
# Within an asyncio event loop
await validation_protocol(websocket)
```

---

### `handle_miner_response`

**Purpose:** Process miner responses to tasks.

**Process:**

1. **Task Handling:**
   - Validates the task ID and wallet address.
   - Processes the task output.
2. **Response Handling:**
   - Returns a success message if the task is accepted.
   - Returns an error message if the task is rejected.

**Returns:**

- `success`: Boolean indicating if the task was accepted.
- `message`: String message providing feedback on the task.

**Example Usage:**

```python
success, message = await handle_miner_response(id, wallet_address, output)
# Result: (True, "Task accepted")
```

---

### `task_validation_output`

**Purpose:** Process the output of task validations.

**Process:**

1. **Output Handling:**
   - Validates the task output against predefined criteria.
   - Processes the wallet address and task output (either `tp` or `np`).
2. **Response Handling:**
   - Returns a success message if the output is valid.
   - Returns an error message if the output is invalid.

**Returns:**

- `success`: Boolean indicating if the output was valid.
- `message`: String message providing feedback on the output.

**Example Usage:**

```python
success, message = task_validation_output(wallet_address, tp=tp)
# Result: (True, "Validation successful")
```

---

### Connection Management

**Purpose:** Manage active connections for miners and validators.

**Details:**

- `active_connections`: Set of active miner connections.
- `validator_connections`: Set of active validator connections.
- Limits enforced by `MAX_CONCURRENT_MINERS` and `MAX_CONCURRENT_VALIDATORS`.

**Example Usage:**

```python
active_connections.add(websocket)
validator_connections.add(websocket)
```

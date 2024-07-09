# Protocol Documentation

## (`protocol.py`) Documentation

---

### `is_valid_address`

**Purpose:** Validate a wallet address.

**Parameters:**

- `address`: The wallet address to validate.

**Process:**

1. **Hexadecimal Check:** Tries to convert the address from hex format.
2. **Base58 Check:** Tries to decode the address using Base58.
   - Checks the length and specifier of the decoded bytes.
3. **Error Handling:** Catches and logs any exceptions that occur during validation.

**Returns:**

- `True` if the address is valid.
- `False` if the address is invalid or an error occurs.

**Example Usage:**

```python
is_valid = is_valid_address("some_wallet_address")
# Result: True or False
```

---

### `validator_protocol`

**Purpose:** Handle communication with pools over WebSocket.

#### Inputs:

- **WebSocket Messages**: JSON formatted messages containing the following keys:
  - `type`: `"validateTask"` or `"PING"`
  - `pool_wallet`: The pool's wallet address (optional)
  - `val_id`: Validator ID for tasks (optional)
  - `task_info`: Task information for validation (optional)
  - `pool_ip`: IP address of the pool (optional)
  - `pool_port`: Port of the pool (optional)

#### Outputs:

- **WebSocket Responses**: JSON formatted messages sent back to the client:
  - For invalid pool wallets: `"ERROR: Invalid pool wallet"`
  - For task validation responses: Task details in JSON format or `"ERROR: [message]"`
  - For pings: `"SUCCESS: Ping"`
  - For unknown message types: `"ERROR: Unknown message type"`
  - For invalid message formats: `"ERROR: Invalid message format"`
  - For max connection limit: WebSocket connection closed with reason `"ERROR: Max connection limit reached"`

**Parameters:**

- `websocket`: The WebSocket connection object.

**Process:**

1. **Check Active Connections:** Closes the connection if the maximum number of concurrent pools is reached.
2. **Add Connection:** Adds the WebSocket connection to the active connections set.
3. **Handle Messages:** Processes messages received from the WebSocket.
   - Validates the message type and handles "validateTask" and "PING" messages.
   - Sends appropriate responses back to the validator.
4. **Error Handling:** Catches and logs JSON decoding errors and connection closures.
5. **Remove Connection:** Removes the WebSocket connection from the active connections set when the connection is closed.

**Returns:** None

**Example Usage:**

```python
await validator_protocol(websocket)
# Handles communication with a validator
```

---

### `send_response_to_pool`

**Purpose:** Send a response message to a pool and await their response.

**Parameters:**

- `pool_info`: The URI of the pool.
- `message`: The message to be sent to the pool.
- `val_id`: The ID of the validation task.

**Process:**

1. **Connect to Pool:** Establishes a WebSocket connection to the pool.
2. **Send Message:** Sends the specified message to the pool.
3. **Await Response:** Waits for a response from the pool with a timeout of 60 seconds.
4. **Close Connection:** Closes the WebSocket connection.
5. **Handle Response:** Processes the response from the pool.
6. **Error Handling:** Catches and logs connection errors and timeouts.

**Returns:** None

**Example Usage:**

```python
await send_response_to_pool("ws://pool_uri", "message", "val123")
# Sends a message to the pool and awaits the response
```

---

### `send_ping_to_iNode`

**Purpose:** Send a ping message to an iNode and await their response.

**Parameters:**

- `uri`: The URI of the iNode.
- `message`: The ping message to be sent.

**Process:**

1. **Connect to iNode:** Establishes a WebSocket connection to the iNode.
2. **Send Ping Message:** Sends the ping message to the iNode.
3. **Await Response:** Waits for a response from the iNode with a timeout of 60 seconds.
4. **Log Response:** Logs the response from the iNode.
5. **Error Handling:** Catches and logs connection errors and timeouts.

**Returns:** None

**Example Usage:**

```python
await send_ping_to_iNode("ws://inode_uri", "ping message")
# Sends a ping message to the iNode and awaits the response
```

---

### `send_task_to_iNode`

**Purpose:** Send a task to an iNode and await their response.

**Parameters:**

- `uri`: The URI of the iNode.
- `message`: The task message to be sent.
- `val_id`: The ID of the validation task.

**Process:**

1. **Connect to iNode:** Establishes a WebSocket connection to the iNode.
2. **Send Task Message:** Sends the task message to the iNode.
3. **Await Response:** Waits for a response from the iNode with a timeout of 60 seconds.
4. **Close Connection:** Closes the WebSocket connection.
5. **Handle Response:** Processes the response from the iNode.
6. **Error Handling:** Catches and logs connection errors and timeouts.

**Returns:** None

**Example Usage:**

```python
await send_task_to_iNode("ws://inode_uri", "task message", "val123")
# Sends a task message to the iNode and awaits the response
```

---

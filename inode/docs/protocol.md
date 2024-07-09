# Protocol Documentation

## (`protocol.py`) Documentation

The `iNode_protocol` establishes and manages WebSocket connections, validates messages, and processes tasks or pings. This function ensures that the WebSocket connections adhere to certain constraints and that messages from validators are handled appropriately.

### Constants

- `MAX_CONCURRENT_VALIDATORS` (int): Defines the maximum number of concurrent WebSocket connections allowed. This limit can be set by modifying the `layout.json` configuration.

## Functionality

### Connection Management

When a new WebSocket connection is established, `iNode_protocol` performs the following steps:

1. **Check Connection Limit:**

   - The function checks if the current number of active connections exceeds `MAX_CONCURRENT_VALIDATORS`.
   - If the limit is exceeded, the connection is closed with a reason message: "ERROR: Max connection limit reached".

2. **Add Connection:**

   - If the limit is not exceeded, the new WebSocket connection is added to the `active_connections` set.

3. **Remove Connection:**
   - The connection is removed from the `active_connections` set upon closure or error.

### Message Handling

Upon receiving a message, `iNode_protocol` performs these actions:

1. **Parse Message:**

   - The message is parsed from JSON format. If parsing fails, an error message is sent, and the connection is closed.

2. **Extract Fields:**
   - The following fields are extracted from the parsed message:
     - `type` (str): The type of message, can be `"TASK"` or `"PING"`.
     - `pool_wallet` (str, optional): The wallet address of the pool.
     - `validator_wallet` (str, optional): The wallet address of the validator.
     - `val_id` (str, optional): The identifier of the validator.
     - `ip` (str, optional): The IP address of the validator.
     - `port` (str, optional): The port number of the validator.

### Message Types

#### `TASK`

When the message type is `"TASK"`, the function processes a task:

1. **Check Pool:**

   - If `pool_wallet` is provided, the `find_pool` function is called to verify the pool.
   - If the pool is not found, an error message is sent, and the connection is closed.

2. **Check Validator:**

   - If `validator_wallet` is provided, the `get_validator_percentage` function checks the validator's stake percentage.
   - If the stake is less than 1%, an error message is sent, and the connection is closed.

3. **Update Scores:**
   - The `update_scores` function is called with `pool_wallet` and `validator_wallet` to set the score.
   - On success, a success message is sent, and the connection is closed.
   - On failure, an error message is sent, and the connection is closed.

#### `PING`

When the message type is `"PING"`, the function responds with a pong:

1. **Update Validator Info:**

   - The `update_validator_info` function updates the validator's information using `validator_wallet`, `ip`, and `port`.

2. **Send Pong:**
   - If the update is successful, a "SUCCESS: Pong" message is sent.
   - If the update fails, an error message is sent.

### Error Handling

If an error occurs during message handling or connection management, the WebSocket connection is closed, and an appropriate error message is sent to the client.

---

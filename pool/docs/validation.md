## Validation connection Documentation

### (`validation.py`) Documentation

---

### `read_peers`

**Purpose:** Read peers from a JSON file and validate their details.

**Parameters:**

- `file_path`: The path to the JSON file containing peer details.

**Process:**

1. **Open File:** Opens the specified JSON file for reading.
2. **Read Data:** Parses the JSON data from the file.
3. **Validate Peers:** Iterates over the data to validate and construct peer URIs.
   - Checks if IP and Port are present for each peer.
   - Constructs a WebSocket URI for each valid peer and appends it to the list.
4. **Error Handling:** Logs errors for JSON decoding issues, file not found, and missing IP or Port details.

**Returns:** A list of tuples containing wallet addresses and their corresponding URIs.

**Example Usage:**

```python
peers = read_peers("peers.json")
# Result: [(wallet_address, uri), ...]
```

---

### `read_wallet`

**Purpose:** Read the percentage information for a specific wallet from a JSON file.

**Parameters:**

- `wallet_address`: The wallet address to look up.

**Process:**

1. **Open File:** Opens the `peers.json` file for reading.
2. **Read Data:** Parses the JSON data from the file.
3. **Find Wallet:** Searches for the specified wallet address in the data.
   - Logs and returns the percentage if found.
   - Logs an error if the percentage is missing or the wallet is not found.
4. **Error Handling:** Logs errors for JSON decoding issues and file not found.

**Returns:** The percentage value for the specified wallet address, or `None` if not found or an error occurs.

**Example Usage:**

```python
percentage = read_wallet("wallet123")
# Result: percentage value or None
```

---

### `save_valid_peers_to_json`

**Purpose:** Save valid peers to a JSON file based on specified criteria.

**Parameters:**

- `vals`: A dictionary containing wallet addresses and their details as JSON strings.

**Process:**

1. **Current Time:** Gets the current UTC time and calculates the time four hours ago.
2. **Validate Peers:** Iterates over the provided wallet details.
   - Parses each detail string to a dictionary.
   - Checks the percentage and ping time validity.
   - Adds valid peers to the `valid_peers` dictionary.
3. **Save to File:** Writes the `valid_peers` dictionary to `peers.json`.
4. **Error Handling:** Logs errors for JSON decoding issues and invalid date formats.

**Returns:** None

**Example Usage:**

```python
save_valid_peers_to_json(vals)
# Result: Valid peers saved to peers.json
```

---

### `fetch_validators`

**Purpose:** Fetch validators from a specified URL.

**Parameters:**

- `validators`: The URL to fetch validators from.

**Process:**

1. **Send Request:** Sends an HTTP GET request to the specified URL.
2. **Process Response:** Parses the JSON response if the request is successful.
3. **Error Handling:** Logs errors for HTTP issues, connection errors, timeouts, and other request exceptions.

**Returns:** The JSON response from the server, or an empty list if an error occurs.

**Example Usage:**

```python
validators = fetch_validators("http://0.0.0.0:8001/validators")
# Result: JSON response or []
```

---

### `fetch_peer_periodically`

**Purpose:** Periodically fetch peer information and save valid peers to a JSON file.

**Parameters:**

- `interval`: The interval in seconds between each fetch operation. Default is 600 seconds (10 minutes).

**Process:**

1. **Continuous Loop:** Runs an infinite loop to fetch peer information.
2. **Fetch Validators:** Calls `fetch_validators` to get the latest validator information.
3. **Save Valid Peers:** Calls `save_valid_peers_to_json` to save valid peers to a JSON file.
4. **Sleep Interval:** Waits for the specified interval before the next execution.

**Returns:** None

**Example Usage:**

```python
fetch_peer_periodically(600)
# Result: Periodically fetches and saves valid peers every 10 minutes
```

---

### `fetch_peer_periodically`

**Purpose:** Periodically fetch peer information and save valid peers to a JSON file.

**Parameters:**

- `interval`: The interval in seconds between each fetch operation. Default is 600 seconds (10 minutes).

**Process:**

1. **Continuous Loop:** Runs an infinite loop to fetch peer information.
2. **Fetch Validators:** Calls `fetch_validators` to get the latest validator information.
3. **Save Valid Peers:** Calls `save_valid_peers_to_json` to save valid peers to a JSON file.
4. **Sleep Interval:** Waits for the specified interval before the next execution.

**Returns:** None

**Example Usage:**

```python
fetch_peer_periodically(600)
# Periodically fetches and saves valid peers every 10 minutes
```

---

### `send_response_to_validator`

**Purpose:** Send a response message to a validator and await their response.

**Parameters:**

- `validator_info`: The URI of the validator.
- `message`: The message to be sent to the validator.

**Process:**

1. **Connect to Validator:** Establishes a WebSocket connection to the validator.
2. **Send Message:** Sends the specified message to the validator.
3. **Await Response:** Waits for a response from the validator with a timeout of 60 seconds.
4. **Close Connection:** Closes the WebSocket connection.
5. **Error Handling:** Logs and handles connection errors and timeouts.

**Returns:** The response from the validator, or `None` if an error occurs.

**Example Usage:**

```python
response = await send_response_to_validator("ws://validator_uri", "message")
# Sends a message to the validator and awaits the response
```

---

### `connect`

**Purpose:** Continuously connect to validators and process validation tasks.

**Process:**

1. **Continuous Loop:** Runs an infinite loop to connect to validators and process tasks.
2. **Test API Connection:** Tests the API connection and retries if it fails.
3. **Select Task:** Calls `select_task_for_validation` to select a task for validation.
4. **Read Peers:** Reads peers from the `peers.json` file.
5. **Filter Validators:** Filters validators that have not yet processed the selected task.
6. **Send Task to Validators:** Sends the task to each validator and processes their responses.
7. **Update Processed Validators:** Updates the list of processed validators and removes them from the list of pending validators.
8. **Sleep Interval:** Waits for 120 seconds before the next iteration.
9. **Error Handling:** Logs and handles unexpected errors during the process.

**Returns:** None

**Example Usage:**

```python
await connect()
# Continuously connects to validators and processes validation tasks
```

---

### `main`

**Purpose:** Main function to initialize and run the periodic tasks and WebSocket server.

**Process:**

1. **Start Peer Fetching Thread:** Starts a daemon thread to periodically fetch peer information.
2. **Start WebSocket Server:** Starts a WebSocket server for validation protocol.
3. **Run Connection Function:** Calls `connect` to continuously process validation tasks.
4. **Shutdown Handling:** Logs the shutdown process when the program exits.

**Returns:** None

**Example Usage:**

```python
await main()
# Initializes and runs periodic tasks and WebSocket server
```

---

### `__main__`

**Purpose:** Entry point for the script to run the main function.

**Process:**

1. **Test Connections:** Tests MongoDB and API connections.
   - Exits if connections fail.
2. **Run Main Function:** Uses `asyncio.run` to execute the `main` function.
3. **Keyboard Interrupt Handling:** Logs shutdown information if interrupted.

**Returns:** None

**Example Usage:**

```python
if __name__ == "__main__":
    asyncio.run(main())
# Entry point to run the main function
```

---

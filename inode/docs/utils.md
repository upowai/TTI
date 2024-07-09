# utils Documentation

## (`layout.py`) Documentation

Purpose: Load and parse a JSON configuration file, handling potential errors gracefully.

### Process:

1. **File Opening**: Attempts to open the specified file path.
2. **JSON Decoding**: Parses the content of the file as JSON.
3. **Error Handling**:
   - **FileNotFoundError**: Prints an error message if the file is not found and exits the program.
   - **JSONDecodeError**: Prints an error message if the JSON format is incorrect and exits the program.
   - **General Exception**: Catches any other unexpected errors, prints an error message, and exits the program.

### Key Functions:

- **open(file_path, "r")**: Opens the file in read mode.
- **json.load(file)**: Parses the content of the file as JSON.
- **exit(1)**: Exits the program with a status code of 1 in case of an error.

### Example Usage:

```python
# Load the configuration from the layout.json file
base = load_config("layout.json")
```

---

# Configuration Guide for layout.json

This guide explains the purpose and structure of the `layout.json` configuration file. It outlines the key sections and parameters that users can adjust to suit their requirements.

## Configuration Sections

### 1. FAST_API

**Purpose**: Configures the FastAPI server settings.

- **FAST_API_URL**: The IP address where the FastAPI server will run.
  - Example: `"0.0.0.0"`
- **FAST_API_PORT**: The port number for the FastAPI server.
  - Example: `8001`

### 2. MONGOD_DB

**Purpose**: Specifies the MongoDB connection settings.

- **MONGO_URL**: The MongoDB connection string.
  - Example: `"mongodb://localhost:27017/"`

### 3. RATE_LIMIT

**Purpose**: Sets the rate limits for API requests.

- **RATE_LIMIT1**: Primary rate limit rule.
  - Example: `"10/minute"`
- **RATE_LIMIT2**: Secondary rate limit rule.
  - Example: `"1/minute"`

### 4. AWARD_SYSTEM

**Purpose**: Defines the reward distribution percentages.

- **FEE**: The percentage fee.
  - Example: `"18%"`
- **POOLS_REWARD**: The percentage of rewards allocated to pools.
  - Example: `"41%"`
- **VALIDATORS_REWARD**: The percentage of rewards allocated to validators.
  - Example: `"41%"`

### 5. URLS

**Purpose**: Contains various API endpoints.

- **API_URL**: Base API URL.
  - Example: `"https://api.upow.ai"`
- **VALIDATORS_URL**: URL to fetch validator information.
  - Example: `"https://api.upow.ai/get_validators_info?inode="`
- **config_3**: Additional configurable URL.
  - Example: `"value_3"`

### 6. TIME

**Purpose**: Configures time intervals for various processes.

- **CHECK_INTERVAL**: Interval for checking processes (in seconds).
  - Example: `60`
- **PUSH_TX**: Interval for pushing transactions (in seconds).
  - Example: `60`
- **FETCH_VALIDATORS**: Interval for fetching validator data (in seconds).
  - Example: `600`
- **DECAY**: Decay interval (in seconds).
  - Example: `600`

### 7. INODE_MAIN_SOCKET

**Purpose**: Sets the main socket connection details.

- **IP**: IP address for the main socket.
  - Example: `"0.0.0.0"`
- **PORT**: Port number for the main socket.
  - Example: `"5501"`

### 8. INODE_WALLETS

**Purpose**: Specifies wallet addresses.

- **WALLET_ADDRESS**: Main wallet address.
  - Example: `"Dsykm6pDTkD93Mx6fh8RBnXi47p2aWy7aaYNKGawjBPYq"`
- **REWARD_ADDRESS**: Reward wallet address.
  - Example: `"Dvhg47J4J2ZgAujAZEJh4PihbWqbyR5BeUKJccNcs7QjC"`

### 9. REWARD_TRACKING

**Purpose**: Configures reward tracking settings.

- **BLOCK_HEIGHT**: The block height to start tracking rewards from.
  - Example: `20001`

### 10. MAX_CONCURRENT

**Purpose**: Sets the maximum number of concurrent validators.

- **VALIDATORS**: Maximum number of validators.
  - Example: `1500`

This configuration file can be adjusted as needed to fit specific deployment environments and requirements.

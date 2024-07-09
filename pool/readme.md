# uPow pool

## Configuration

Before diving into the MinerPool setup, it's essential to configure the system correctly. The `config.py` file contains several critical settings that need to be adjusted according to your network setup and preferences.

## Enable port for accepting connections (Ubuntu)

```bash
  sudo ufw allow 5503
```

## Installing Mongodb

To Install Mongodb on Ubuntu you can use the `install_mongodb.sh` script.

### Ubuntu

1. **Make the Script Executable:**

   - Open a terminal and navigate to the directory containing the `install_mongodb.sh` script.
   - Run the command `chmod +x install_mongodb.sh` to make the script executable.

2. **Run the Script:**
   - Execute the script by running `./install_mongodb.sh` in the terminal.
   - If necessary, the script will ask for your password to grant permission for installation steps that require superuser access.

## Getting Started

To get started with MinerPool, ensure that Python 3.6+ is installed on your system. Follow these steps:

1. **Navigate to the Project Directory:**

   ```bash
   cd pool
   ```

2. **Install Dependencies:**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure Settings**: Adjust the settings in `config.py` as per your setup.
4. \*_Configure MongoDB _
   - Ensure MongoDB is running on your system.
   - Update the MongoDB connection URL and database details in `layout.json` if necessary.
5. **Set Up Environment Variables:**

   - Set up environment variables for configuration parameters.
   - Open `.env` file in your project root directory you can use command `nano .env`
   - Add the following lines to your `.env` file,`PRIVATEKEY=YOUR_POOL_WALLET_PRIVATEKEY`

     ```
      PRIVATEKEY=key

     ```

6. **Prepare Your Development Environment**

   Depending on your operating system, you may need to install additional tools to ensure the `fastecdsa` Python package and other dependencies compile correctly:

   - **Ubuntu Users:**

     Install the necessary libraries by running:

     ```bash
     sudo apt-get update
     sudo apt-get install libgmp3-dev
     sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
     ```

7. **Run Pool**: Start the Pool server by running the main script. For example, `python3 main.py`.
8. **Connect with Validators**: Start by running `python3 validation.py`.

## Configuration Sections (`layout.json`)

#### 1. FAST_API

**Purpose**: Configures the FastAPI server settings.

- **FAST_API_URL**: The IP address where the FastAPI server will run.
  - Example: `"0.0.0.0"`
- **FAST_API_PORT**: The port number for the FastAPI server.
  - Example: `8003`

#### 2. MONGOD_DB

**Purpose**: Configures the MongoDB database connection settings.

- **MONGO_URL**: The URL for connecting to the MongoDB instance.
  - Example: `"mongodb://localhost:27017/"`

#### 3. WHITE_LIST

**Purpose**: Configures the whitelist settings.

- **ACTIVE**: Indicates if the whitelist is active.
  - Example: `"False"`
- **DEFAULT_DIFFICULTY**: Default difficulty level for mining.
  - Example: `5`
- **BASE_MINER_COUNT**: Base count of miners.
  - Example: `1`
- **INCREASE_DIFFICULTY**: Difficulty increase step.
  - Example: `100`
- **MAX_MINERS**: Maximum number of miners allowed.
  - Example: `5`
- **IMMUNITY**: Immunity period in seconds.
  - Example: `600`

#### 4. RATE_LIMIT

**Purpose**: Sets rate limiting for API requests.

- **RATE_LIMIT1**: First rate limit rule.
  - Example: `"10/minute"`
- **RATE_LIMIT2**: Second rate limit rule.
  - Example: `"1/minute"`

#### 5. AWARD_SYSTEM

**Purpose**: Configures the reward distribution system.

- **FEE**: The fee percentage.
  - Example: `"18%"`
- **MINER_REWARD**: The percentage of rewards allocated to miners.
  - Example: `"82%"`

#### 6. URLS

**Purpose**: Stores various API URLs.

- **API_URL**: The base URL for the API.
  - Example: `"https://api.upow.ai"`
- **config_2**: Additional configuration value.
  - Example: `"value_2"`
- **config_3**: Additional configuration value.
  - Example: `"value_3"`

#### 7. TIME

**Purpose**: Configures time intervals for various processes.

- **CHECK_INTERVAL**: Interval for checking status.
  - Example: `60` (seconds)
- **PUSH_TX**: Interval for pushing transactions.
  - Example: `60` (seconds)
- **GEN_VALIDATION_TASK**: Interval for generating validation tasks.
  - Example: `60` (seconds)
- **VALIDATION_DELETE_TIMER**: Timer for deleting validation tasks.
  - Example: `600` (seconds)

#### 8. POOL_MAIN_SOCKET

**Purpose**: Configures the main socket settings for the pool.

- **IP**: The IP address for the pool main socket.
  - Example: `"0.0.0.0"`
- **PORT**: The port number for the pool main socket.
  - Example: `5503`

#### 9. POOL_VALIDATION_SOCKET

**Purpose**: Configures the validation socket settings for the pool.

- **IP**: The IP address for the pool validation socket.
  - Example: `"0.0.0.0"`
- **PORT**: The port number for the pool validation socket.
  - Example: `5505`

#### 10. INODE_INFO

**Purpose**: Configures the URL for inode information.

- **URL**: The URL for accessing inode validator information.
  - Example: `"http://0.0.0.0:8001/validators"`

#### 11. POOL_WALLETS

**Purpose**: Configures wallet addresses for the pool.

- **POOL_ADDRESS**: The main pool address.
  - Example: `"Dsykm6pDTkD93Mx6fh8RBnXi47p2aWy7aaYNKGawjBPYq"`
- **POOL_REWARD_ADDRESS**: The address for receiving pool rewards.
  - Example: `"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`

#### 12. REWARD_TRACKING

**Purpose**: Configures the starting block height for reward tracking.

- **BLOCK_HEIGHT**: The block height from which to start tracking rewards.
  - Example: `20001`

#### 13. MAX_CONCURRENT

**Purpose**: Sets the maximum number of concurrent miners and validators.

- **MINERS**: Maximum number of concurrent miners allowed.
  - Example: `1500`
- **VALIDATORS**: Maximum number of concurrent validators allowed.
  - Example: `1500`

---

## API Endpoints

MinerPool offers a set of RESTful API endpoints through its FastAPI server, allowing for various operations related to wallet balance management and transaction processing. Below are the available endpoints:

### Wallet Balance

- **GET `/get_balance/`**: Retrieve the current balance of a specified miner's wallet address.

  - **Parameters**:
    - `wallet_address`: The wallet address of the miner.
  - **Returns**: The balance of the specified wallet address.

- **GET `/get_balance_poolowner/`**: Fetch the balance of the pool owner's wallet.
  - **Returns**: The balance of the pool owner's wallet.

### Balance Deduction

- **POST `/deduct_balance/`**: Deduct a specified amount from a miner's wallet balance.

  - **Body**:
    - `wallet_address`: The wallet address from which the balance will be deducted.
    - `amount_to_deduct`: The amount to be deducted from the wallet balance.
  - **Returns**: A message indicating the successful deduction of the specified amount.

- **POST `/poolowner_deduct_balance/`**: Deduct a specified amount from the pool owner's wallet balance.
  - **Body**:
    - `amount_to_deduct`: The amount to be deducted from the pool owner's wallet balance.
  - **Returns**: A message indicating the successful deduction of the specified amount.

### Sample API Call using `curl`

To test the `/get_balance/` endpoint to retrieve the balance of a specific wallet address, you can use the following `curl` command:

```bash
curl -X 'GET' \
  'http://<FAST_API_URL>:<FAST_API_PORT>/get_balance/?wallet_address=DhWyMUj2pna2UYbvrqULyLf6dEo2MNzPHA7Uh4kBrJGFY' \
  -H 'accept: application/json'
```

Replace `<FAST_API_URL>` and `<FAST_API_PORT>` with the actual URL and port where your FastAPI server is running. This command sends a GET request to the `/get_balance/` endpoint with a query parameter for the `wallet_address`. The server should respond with the balance of the specified wallet address in JSON format.

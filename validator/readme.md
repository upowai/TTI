# uPow Validator

## Prerequisites

Before setting up the Validator Server, ensure you have the following installed:

- Python 3.10 or higher
- MongoDB
- Required Python libraries (listed in `requirements.txt`)

## Configuration

Before you start, ensure you have correctly set up your environment. The `config.py` file contains essential settings that you must review and configure according to your setup.

Please check envExample file to set `.env`

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

## Installation

1. **Navigate to the Project Directory:**

   ```bash
   cd validator
   ```

2. **Install Dependencies:**

   ```bash
   pip3 install -r requirements.txt
   ```

43 **Review and update the `config.py` file with your specific settings.**

5. **Configure MongoDB **

   - Ensure MongoDB is running on your system.
   - Update the MongoDB connection URL and database details in `layout.json` if necessary.

6. **Set Up Environment Variables:**

   - Set up environment variables for configuration parameters.
   - Open `.env` file in your project root directory you can use command `nano .env`
   - Add the following lines to your `.env` file,`PRIVATEKEY=YOUR_VALIDATOR_WALLET_PRIVATEKEY` you check envExample for reference

     ```
      PRIVATEKEY=key
     ```

7. **Prepare Your Development Environment**

   Depending on your operating system, you may need to install additional tools to ensure the `fastecdsa` Python package and other dependencies compile correctly:

   - **Ubuntu Users:**

     Install the necessary libraries by running:

     ```bash
     sudo apt-get update
     sudo apt-get install libgmp3-dev
     sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
     ```

## Running the Validator

To start

the validator node, navigate to the repository's root directory and execute the following command:

**Run Validator **: Start the Validator server by running the main script. For example, `python3 main.py`.

---

## Configuration Sections (`layout.json`)

#### 1. FAST_API

**Purpose**: Configures the FastAPI server settings.

- **FAST_API_URL**: The IP address where the FastAPI server will run.
  - Example: `"0.0.0.0"`
- **FAST_API_PORT**: The port number for the FastAPI server.
  - Example: `8002`

#### 2. MONGOD_DB

**Purpose**: Configures the MongoDB database connection settings.

- **MONGO_URL**: The URL for connecting to the MongoDB instance.
  - Example: `"mongodb://localhost:27017/"`

#### 3. RATE_LIMIT

**Purpose**: Sets rate limiting for API requests.

- **RATE_LIMIT1**: First rate limit rule.
  - Example: `"10/minute"`
- **RATE_LIMIT2**: Second rate limit rule.
  - Example: `"1/minute"`

#### 4. AWARD_SYSTEM

**Purpose**: Configures the reward distribution system.

- **FEE**: The fee percentage.
  - Example: `"18%"`
- **DELEGATE_REWARD**: The percentage of rewards allocated to delegates.
  - Example: `"82%"`

#### 5. URLS

**Purpose**: Stores various API URLs.

- **API_URL**: The base URL for the API.
  - Example: `"https://api.upow.ai"`
- **config_2**: Additional configuration value.
  - Example: `"value_2"`
- **config_3**: Additional configuration value.
  - Example: `"value_3"`

#### 6. TIME

**Purpose**: Configures time intervals for various processes.

- **CHECK_INTERVAL**: Interval for checking status.
  - Example: `60` (seconds)
- **PUSH_TX**: Interval for pushing transactions.
  - Example: `60` (seconds)
- **PING_TIME**: Interval for ping operations.
  - Example: `60` (seconds)

#### 7. VALIDATOR_SOCKET

**Purpose**: Configures the validator socket settings.

- **SERVER_IP**: The IP address for the server.
  - Example: `"0.0.0.0"`
- **IP**: The IP address for the validator socket.
  - Example: `"0.0.0.0"`
- **PORT**: The port number for the validator socket.
  - Example: `5502`

#### 8. INODE_INFO

**Purpose**: Configures the inode information.

- **INODE_IP**: The IP address for the inode.
  - Example: `"0.0.0.0"`
- **INODE_PORT**: The port number for the inode.
  - Example: `5501`

#### 9. VALIDATOR_WALLETS

**Purpose**: Configures wallet addresses for the validator.

- **VAL_ADDRESS**: The main validator address.
  - Example: `"DseZNohbj5NN2XzFUaioufN6jgMNqwQaMYGG2x8rGxkoH"`
- **VAL_REWARD_ADDRESS**: The address for receiving validator rewards.
  - Example: `"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`

#### 10. REWARD_TRACKING

**Purpose**: Configures the starting block height for reward tracking.

- **BLOCK_HEIGHT**: The block height from which to start tracking rewards.
  - Example: `20001`

#### 11. MAX_CONCURRENT

**Purpose**: Sets the maximum number of concurrent pools.

- **POOLS**: Maximum number of concurrent pools allowed.
  - Example: `1500`

---

## API Endpoints

The validator node provides several API endpoints for interaction:

- `/get_balance/`: Retrieve the balance of a given wallet address.
- `/get_balance_validatorowner/`: Get the balance of the validator owner.
- `/deduct_balance/`: Deduct a specified amount from a wallet.
- `/validatorowner_deduct_balance/`: Deduct a specified amount from the validator owner's balance.

These endpoints are accessible via HTTP GET and POST requests to the FastAPI server running on `FAST_API_URL:FAST_API_PORT`.

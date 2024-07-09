# iNode Server Documentation

## Prerequisites

Before setting up the iNode Server, ensure you have the following installed:

- Python 3.9 or higher
- MongoDB
- Required Python libraries (listed in `requirements.txt`)

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
   cd inode
   ```

2. **Install Dependencies:**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure MongoDB**

   - Ensure MongoDB is running on your system.
   - Update the MongoDB connection URL and database details in `layout.json` if necessary.

4. **Set Up Environment Variables:**

   - Optionally, set up environment variables for configuration parameters.

5. **Generate SHA Keys:**

   - First, you need to generate a pair of SHA keys (public and private). Run the following command in your terminal:
     ```bash
     python generatekey.py
     ```
   - This script will generate two keys: a public key and a private key. You will use these keys for secure communication.
   - After generating the SHA keys, you need to set up your environment variables. Specifically, you will set up the private key of your registered Inode wallet.
   - Open `.env` file in your project root directory you can use command `nano .env`
   - Add the following lines to your `.env` file,`PRIVATEKEY=YOUR_INODE_WALLET_PRIVATEKEY` you check envExample for reference
     ```
     SHA_PRIVATEKEY=YOUR_SHA_PRIVATE_KEY
     SHA_PUBLICKEY=YOUR_SHA_PUBLIC_KEY
     PRIVATEKEY=YOUR_INODE_WALLET_PRIVATEKEY
     ```

6. **Prepare Your Development Environment**

   Depending on your operating system, you may need to install additional tools to ensure the `fastecdsa` Python package and other dependencies compile correctly:

   Install the necessary libraries by running:

   ```bash
   sudo apt-get update
   sudo apt-get install libgmp3-dev
   sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
   ```

---

### Configuration Sections (`layout.json`)

#### 1. FAST_API

**Purpose**: Configures the FastAPI server settings.

- **FAST_API_URL**: The IP address where the FastAPI server will run.
  - Example: `"0.0.0.0"`
- **FAST_API_PORT**: The port number for the FastAPI server.
  - Example: `8001`

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
- **POOLS_REWARD**: The percentage of rewards allocated to pools.
  - Example: `"41%"`
- **VALIDATORS_REWARD**: The percentage of rewards allocated to validators.
  - Example: `"41%"`

#### 5. URLS

**Purpose**: Stores various API URLs.

- **API_URL**: The base URL for the API.
  - Example: `"https://api.upow.ai"`
- **VALIDATORS_URL**: The URL for fetching validator information.
  - Example: `"https://api.upow.ai/get_validators_info?inode="`
- **config_3**: Additional configuration value.
  - Example: `"value_3"`

#### 6. TIME

**Purpose**: Configures time intervals for various processes.

- **CHECK_INTERVAL**: Interval for checking status.
  - Example: `60` (seconds)
- **PUSH_TX**: Interval for pushing transactions.
  - Example: `60` (seconds)
- **FETCH_VALIDATORS**: Interval for fetching validator information.
  - Example: `600` (seconds)
- **DECAY**: Interval for decay process.
  - Example: `600` (seconds)

#### 7. INODE_MAIN_SOCKET

**Purpose**: Configures the main socket settings for the inode.

- **IP**: The IP address for the inode main socket.
  - Example: `"0.0.0.0"`
- **PORT**: The port number for the inode main socket.
  - Example: `5501`

#### 8. INODE_WALLETS

**Purpose**: Configures wallet addresses for the inode.

- **WALLET_ADDRESS**: The main wallet address.
  - Example: `"Dsykm6pDTkD93Mx6fh8RBnXi47p2aWy7aaYNKGawjBPYq"`
- **REWARD_ADDRESS**: The address for receiving rewards.
  - Example: `"Dvhg47J4J2ZgAujAZEJh4PihbWqbyR5BeUKJccNcs7QjC"`

#### 9. REWARD_TRACKING

**Purpose**: Configures the starting block height for reward tracking.

- **BLOCK_HEIGHT**: The block height from which to start tracking rewards.
  - Example: `20001`

#### 10. MAX_CONCURRENT

**Purpose**: Sets the maximum number of concurrent validators.

- **VALIDATORS**: Maximum number of concurrent validators allowed.
  - Example: `1500`

---

## Running the Server

**Start the iNode Server:**

- Run the following command in the project directory:
  ```bash
  python3 main.py
  ```
- This will start the FastAPI server and the socket-based server for handling client connections.

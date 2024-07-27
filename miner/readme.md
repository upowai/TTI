# TTI Miner

This TTI Miner is designed to connect with mining pools, receive computational tasks, process them, and return the results to the pool efficiently.

## Features

- **Seamless Pool Connection**: Connects to specified mining pools using WebSocket.
- **Task Processing**: Receives and processes computational tasks with high efficiency.
- **Automated Submission**: Submits computed results back to the pool automatically.

## Prerequisites

Ensure the following are installed before starting:

- Python 3.11 or higher
- `pip` for Python package management
- An active internet connection

## Installation

Follow these steps to install TTI Miner:

### 1. Clone the Repository

Clone the Miner repository to your local machine:

```bash
git clone https://github.com/upowai/TTI-MINER.git
```

### 2. Install Dependencies

Navigate to the cloned directory and install the required Python packages:

```bash
cd TTI-MINER
python3.11 -m venv miner
source miner/bin/activate
pip3 install -r requirements.txt
```

### 3. Make the Script Executable

Make the setup script executable:

```bash
chmod +x ./run_setup.sh
```

### 4. Run the Setup Script

Run the setup script to download necessary models and perform the required setup:

```bash
./run_setup.sh
```

## Configuration

TTI Miner requires specific command-line arguments to start:

- `--MINER_POOL_IP`: The IP address of the mining pool.
- `--MINER_POOL_PORT`: The port number of the mining pool.
- `--WALLET_ADDRESS`: Your wallet address for receiving mining rewards.
- `--ENDPOINT`: The endpoint for communication (default: `"http://192.99.7.175:9003"`).
- `--DEVICE`: GPU device number for computation.

## Usage

To run TTI Miner, use the following command:

```bash
python miner.py --WALLET_ADDRESS "your_wallet_address" --MINER_POOL_IP "192.99.7.175" --MINER_POOL_PORT 4403 --ENDPOINT "http://192.99.7.175:9003" --DEVICE 0
```

Replace `"192.99.7.175"`, `4403`, and `"your_wallet_address"` with the appropriate miner pool IP, port, and your wallet address.

## Contributing

Contributions are welcome! Please ensure your code adheres to the project's coding standards and includes appropriate tests.

---

By following these steps, you'll be able to set up and run your TTI Miner seamlessly. Happy mining!

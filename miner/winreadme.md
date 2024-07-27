# TTI-Miner Windows (Might not work - not tested)

Follow these steps to set up and run the TTI-Miner on your windows.

## Step 1: Clone the Repository

First, you need to clone the TTI-Miner repository from GitHub.

```bash
git clone https://github.com/upowai/TTI-MINER.git
```

## Step 2: Navigate to the Cloned Directory

Move inside the cloned directory.

```bash
cd TTI-MINER
```

## Step 3: Check GPU Compatibility

Verify if your GPU is working correctly by checking the CUDA version.

```bash
nvcc --version
```

## Step 4: Check Python Version

Ensure you have Python 3.11 installed on your system.

```bash
python --version
```

If you don't have Python 3.11, you can download and install it.

## Step 5: Create a Virtual Environment

Create a virtual environment to manage dependencies.

```bash
python -m venv myenv
```

## Step 6: Activate the Virtual Environment

Activate your newly created virtual environment.

### On Windows

```bash
myenv\Scripts\activate
```

## Step 7: Install Dependencies

Install all the necessary dependencies listed in the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

## Step 8: Run Setup Script

Execute the setup script to download the required model and install everything needed TTI iNode.

```bash
python winsetup.py
```

## Step 9: Run the Miner

Finally, run the miner with your wallet address and the miner pool details.

```bash
python miner.py --WALLET_ADDRESS "E3sGYEhVznzmjFGv99bhqWQrRoKsbRUuRwYJRHEUtxnek" --MINER_POOL_IP "192.99.7.175" --MINER_POOL_PORT 4403 --ENDPOINT "http://192.99.7.175:9003" --DEVICE 0
```

Replace the wallet address

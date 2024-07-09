# Transactions Documentation

## (`batch.py`) Documentation

This documentation provides details on the transaction processing system implemented using Python and MongoDB. It includes two main components:

1. **Batch Processing (`batch.py`)**: Handles the retrieval, filtering, and processing of transactions.
2. **Transaction Signing and Pushing (`payment.py`)**: Manages the signing and pushing of transactions to the blockchain.

## Setup

## Batch Processing (`batch.py`)

### Purpose

`batch.py` handles the retrieval and processing of transactions from the `tempWithdrawals` collection in MongoDB. It ensures that transactions are unique per wallet address and processes a batch of up to 15 transactions at a time.

### Functions

#### `process_all_transactions()`

- **Description**: Main function to process all pending transactions.
- **Steps**:

  1. **API Connection Check**: Verifies the connection to the blockchain API.
  2. **Transaction Retrieval**: Fetches all transactions from `tempWithdrawals`, sorted by timestamp.
  3. **Uniqueness Enforcement**: Filters transactions to ensure only the latest transaction per wallet address is processed.
  4. **Transaction Processing**: Processes up to 15 transactions asynchronously.

- **Example**:

  ```python
  def update_balance_periodically():
    try:
        while True:
            process_all_transactions()
            time.sleep(base["TIME"]["PUSH_TX"])
    except Exception as e:
        print(f"Error in update_balance_periodically: {e}")
  ```

### Modifications

- **Batch Size**: Adjust the number of transactions processed by changing the slice in `pending_transactions`.

  ```python
  pending_transactions = list(unique_transactions.values())[:n]  # Change `n` to desired batch size

  ```

- **Transaction Sorting**: Modify the sorting criteria if a different order of processing is required.

  ```python
  all_transactions = list(tempWithdrawals.find().sort("timestamp", 1))
  ```

---

## (`payment.py`) Documentation

### Transaction Signing and Pushing

`payment.py` handles the actual signing of transactions and pushing them to the blockchain. It also deals with transaction splitting and error handling.

### Functions

#### `sign_and_push_transactions(transactions)`

- **Description**: Signs and pushes a list of transactions to the blockchain.
- **Parameters**: `transactions` - List of transactions to process.
- **Steps**:

  1. **Iterate Transactions**: Loops through each transaction to sign and push.
  2. **Send Transaction**: Uses the `upow.send_transaction` method.
  3. **Update MongoDB**: Updates the `submittedTransactions` or `errorTransactions` collection based on the result.
  4. **Transaction Splitting**: Splits transactions if errors related to UTXO limits or URI lengths occur.

- **Example**:

  ```python
  asyncio.run(sign_and_push_transactions(transactions))
  ```

#### `round_up_decimal_new(decimal, round_up_length)`

- **Description**: Rounds a decimal value up to a specified precision.
- **Parameters**: `decimal` - Decimal value to round, `round_up_length` - Precision string (e.g., "0.00000001").

#### `add_transaction_to_batch(wallet_address, tokens_to_distribute, rewardType)`

- **Description**: Adds a new transaction to the `tempWithdrawals` collection.
- **Parameters**: `wallet_address`, `tokens_to_distribute`, `rewardType`.

### Modifications

- **Error Handling**: Add custom error handling logic in the `sign_and_push_transactions` function to handle additional error cases.
- **Transaction Splitting Logic**: Modify the logic for splitting transactions if different criteria or strategies are needed.

  ```python
  split_amount = round_up_decimal_new(amount / n)  # Adjust `n` for custom splitting logic
  ```

## Error Handling

- **Error Logging**: Errors are logged using Python’s `logging` module.
- **Transaction Errors**: Failed transactions are recorded in the `errorTransactions` collection.
- **Retry Mechanism**: The current implementation retries by splitting transactions based on error messages related to UTXO limits and URI lengths.

---

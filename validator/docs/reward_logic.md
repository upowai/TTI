## Reward_logic Documentation

## (`delegates_reward.py`) Documentation

### `update_delegate_balances`

**Purpose:** Update the balances of delegates based on their percentage share of a specified amount and store the updates in the database.

**Parameters:**

- `amount`: The total amount to be distributed among delegates.
- `sorted_delegates`: A list of delegate information, where each entry contains the delegate's identifier and their percentage share.
- `block_range_str`: A string representing the block range for which the updates are being made.

**Process:**

1. **Convert Amount to Decimal:** Converts the provided `amount` to a `Decimal` for precise calculations.
2. **Initialize Update Dictionary:** Initializes a dictionary `delegate_updates` to store the update details for each delegate.
3. **Iterate Over Delegates:** Iterates over the list of delegates to calculate and update their balances.
   - **Validate Delegate Information:** Checks if the delegate and percentage information is present and valid.
   - **Calculate Amount to Add:** Calculates the amount to be added to the delegate's balance based on their percentage share.
   - **Skip Small Amounts:** Skips processing if the calculated amount is too small.
   - **Fetch Current Balance:** Retrieves the current balance of the delegate from the `userStats` collection in MongoDB.
   - **Update Balance:** Updates or inserts the new balance for the delegate in the `userStats` collection.
   - **Record Update Details:** Records the previous balance, added amount, and new balance in the `delegate_updates` dictionary.
4. **Store Updates in Database:** Calls `store_in_db` to store the update details in the database and `retrieve_from_db` to verify the updates.
5. **Error Handling:** Catches and logs any exceptions that occur during the process.

**Returns:** None

**Example Usage:**

```python
update_delegate_balances(1000, sorted_delegates, "1000-1010")
# Updates delegate balances based on their percentage share of 1000 units
```

---

## (`percentage.py`) Documentation

### `round_up_decimal_new`

**Purpose:** Round a decimal number to a specified precision.

**Parameters:**

- `decimal`: The `Decimal` number to be rounded.
- `round_up_length`: (Optional) A `str` indicating the precision for rounding. Default is `"0.00000001"`.

**Process:**

1. **Quantization:** Rounds the provided `decimal` to the precision defined by `round_up_length` using `Decimal.quantize`.

**Returns:** The rounded `Decimal` number.

**Example Usage:**

```python
rounded_value = round_up_decimal_new(Decimal("0.123456789"))
# Result: Decimal('0.12345679')
```

---

### `percentage_match`

**Purpose:** Validate that the total of validator fee, delegates reward percentages equals 100%.

**Process:**

1. **Retrieve Percentages:** Fetches the percentage values for fee, delegates rewards from the `base` configuration.
2. **Convert to Decimal:** Converts the string percentage values to `Decimal` after removing the '%' sign.
3. **Total Validation:** Checks if the sum of the percentages equals 100%.

**Returns:**

- `True` if the total percentage equals 100%.
- `False` if the total percentage does not equal 100% or if an error occurs (e.g., missing keys).

**Key Error Handling:**

- Logs an error if a key is not found or an unexpected exception occurs.

**Example Usage:**

```python
is_valid = percentage_match()
# Result: True or False
```

---

### `calculate_percentages`

**Purpose:** Calculate the distribution of a total amount based on predefined percentages for validator fees and delegates rewards.

**Parameters:**

- `total_amount`: The total amount (as a `Decimal` or convertible to `Decimal`) to be distributed.

**Process:**

1. **Retrieve Percentages:** Fetches the percentage values for validator fees, and delegates rewards from the `base` configuration.
2. **Convert to Decimal:** Converts the string percentage values to `Decimal` after removing the '%' sign.
3. **Total Validation:** Validates that the sum of the percentages equals 100%.
4. **Calculate Shares:** Divides the `total_amount` into portions based on the percentages:
   - Fee
   - Delegate reward
5. **Round Shares:** Rounds each portion using `round_up_decimal_new`.

**Returns:**

- A dictionary with the keys `"18%"`, `"82%"`, representing the fee, delegate reward portions respectively.
- `False` if the total percentage does not equal 100%.

**Example Usage:**

```python
shares = calculate_percentages(Decimal("1000"))
# Result: {'18%': Decimal('18.00000000'), '82%': Decimal('82.00000000')}
```

---

## (`process_blocks.py`) Documentation

### `record_block_transactions`

**Purpose:** Record a block transaction hash in the database if it doesn't already exist.

**Parameters:**

- `hash_value`: The hash value of the transaction to be recorded.

**Process:**

1. **Database Update:** Attempts to insert the transaction hash into the `blockTransactions` collection using `upsert=True`.
   - If the transaction hash is new, it will be inserted.
   - If the transaction hash already exists, it logs a message and does not insert it again.
2. **Error Handling:** Logs and returns `None` if a `PyMongoError` occurs.

**Returns:**

- `True` if a new transaction is inserted.
- `False` if the transaction already exists.
- `None` if an error occurs.

**Example Usage:**

```python
success = record_block_transactions("hash123")
# Result: True, False, or None
```

---

### `analyze_block_rewards`

**Purpose:** Analyze blocks to calculate and distribute rewards based on the transactions.

**Process:**

1. **Percentage Validation:** Calls `percentage_match` to ensure the predefined percentages sum to 100%.
2. **Fetch Last Block Height:** Retrieves the last processed block height from the database or uses a hardcoded value if none is found.
3. **Fetch Block Data:** Uses `fetch_block` to get block details starting from the last processed block height.
   - Logs and returns `None` if no block data is retrieved or if there are no new blocks.
4. **Transaction Analysis:** Iterates over the transactions in each block:
   - Checks for relevant transactions (type "REGULAR" and addresses matching the validator wallet).
   - Records new transactions and sums their amounts.
5. **Update Last Block Height:** Updates the last processed block height in the database if new blocks are processed.
6. **Calculate Percentages:** Calls `calculate_percentages` to determine the reward distribution.
7. **Error Handling:** Logs errors and returns `None` if an exception occurs.

**Returns:**

- A tuple `(percentages, block_range_str)` if successful.
- `None` if no relevant transactions are found or if an error occurs.

**Example Usage:**

```python
info = analyze_block_rewards()
# Result: (percentages, block_range_str) or None
```

---

### `process_block_rewards`

**Purpose:** Process block rewards by analyzing block data, fetching delegate information, and updating balances.

**Process:**

1. **Fetch Delegate Information:** Calls `fetch_all_delegate_info` to get the list of delegates.
   - Calls `sort_delegates` to sort the delegate information.
2. **Analyze Block Rewards:** Calls `analyze_block_rewards` to get the reward percentages and block range.
   - If `None` is returned, logs a message and skips reward processing.
3. **Distribute Rewards:** Calls the update functions to distribute the rewards:
   - `update_delegate_balances` for delegate rewards.
   - `update_entityOwners_reward` for validator rewards.
4. **Logging:** Logs the reward amounts for delegates and validators.
5. **Error Handling:** Logs errors if any exceptions occur during the process.

**Returns:** None

**Example Usage:**

```python
process_block_rewards()
# Result: None
```

---

## (`val_reward.py`) Documentation

---

### `update_entityOwners_reward`

**Purpose:** Update the reward amount for the entity owners.

**Parameters:**

- `amount`: The amount to be added to the entity owners' current balance.

**Process:**

1. **Convert Amount to Decimal:** Converts the provided `amount` to a `Decimal` for precise calculations.
2. **Fetch Current Entry:** Attempts to find the current entry for `entityOwners` in the `entityOwners` collection.
   - If the entry exists, retrieves the current amount and wallet address.
   - If the entry does not exist, initializes the current amount to `0.0` and uses the default wallet address from the `base` configuration.
3. **Calculate New Amount:** Adds the provided amount to the current amount and rounds the result using `round_up_decimal_new`.
4. **Get Current Time:** Retrieves the current UTC time in ISO format.
5. **Update Database:** Updates the `entityOwners` document in the database with the new amount, current time, and wallet address. Uses `upsert=True` to create the document if it does not exist.
6. **Error Handling:** Logs any exceptions that occur during the process.

**Returns:** None

**Example Usage:**

```python
update_entityOwners_reward(1000)
# Updates the entity owners' reward amount by adding 1000 units
```

---

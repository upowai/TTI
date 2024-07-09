# Reward_logic Documentation

## (`emission.py`) Documentation

### `pool_emission`

**Purpose:** Distribute rewards to pools based on their scores.

**Process:**

1. **Database Check:** Queries the database to find pools with a positive score.
2. **Score Calculation:** Accumulates the total score of all valid pools.
   - If no pools have a positive score, the function exits early with a message.
   - If the total score is zero, the function exits early with a message.
3. **Batch Processing:** Processes pools in batches (defined by `batch_size`) to distribute the reward amount proportionally based on their score.
4. **Transaction Addition:** Uses the `add_transaction_to_batch` function to add transactions to the batch for each pool.
5. **Store Updates:** Converts all `Decimal` values to `float` and stores the updates in the database using `store_in_db`.

**Key Functions:**

- `add_transaction_to_batch(pool_address, amount, "pool_reward")`
- `store_in_db(block_range, pool_updates)`

---

### `validator_emission`

**Purpose:** Distribute rewards to validators based on their percentage scores.

**Process:**

1. **Database Check:** Queries the database to find validators with a score of 1.
2. **Batch Processing:** Processes validators in batches (defined by `batch_size`) to distribute the reward amount proportionally based on their percentage.
   - If no validators with a score of 1 are found, the function exits early with a message.
3. **Transaction Addition:** Uses the `add_transaction_to_batch` function to add transactions to the batch for each validator.
4. **Logging:** Logs the successful addition of validator transactions.

**Key Functions:**

- `add_transaction_to_batch(wallet_address, amount, "validator_reward")`

---

### `iNode_emission`

**Purpose:** Distribute rewards to the iNode reward wallet.

**Process:**

1. **Reward Calculation:** Calculates the total reward amount.
2. **Transaction Addition:** Uses the `add_transaction_to_batch` function to add a transaction to the batch for the iNode wallet.
3. **Logging:** Logs the successful processing of the iNode reward.

**Key Functions:**

- `add_transaction_to_batch(REWARD_ADDRESS, amount, "iNode_reward")`

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

**Purpose:** Validate that the total of fee, pool reward, and validator reward percentages equals 100%.

**Process:**

1. **Retrieve Percentages:** Fetches the percentage values for fees, pool rewards, and validator rewards from the `base` configuration.
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

**Purpose:** Calculate the distribution of a total amount based on predefined percentages for fees, pool rewards, and validator rewards.

**Parameters:**

- `total_amount`: The total amount (as a `Decimal` or convertible to `Decimal`) to be distributed.

**Process:**

1. **Retrieve Percentages:** Fetches the percentage values for fees, pool rewards, and validator rewards from the `base` configuration.
2. **Convert to Decimal:** Converts the string percentage values to `Decimal` after removing the '%' sign.
3. **Total Validation:** Validates that the sum of the percentages equals 100%.
4. **Calculate Shares:** Divides the `total_amount` into portions based on the percentages:
   - Fee
   - Pools reward
   - Validators reward
5. **Round Shares:** Rounds each portion using `round_up_decimal_new`.

**Returns:**

- A dictionary with the keys `"18%"`, `"41%_1"`, and `"41%_2"` representing the fee, pool reward, and validator reward portions respectively.
- `False` if the total percentage does not equal 100%.

**Example Usage:**

```python
shares = calculate_percentages(Decimal("1000"))
# Result: {'18%': Decimal('180.00000000'), '41%_1': Decimal('410.00000000'), '41%_2': Decimal('410.00000000')}
```

---

## (`reward.py`) Documentation

### `find_pool`

**Purpose:** Check if a pool exists in the database by its address.

**Parameters:**

- `pool_address`: The address of the pool to find.

**Process:**

1. **Database Query:** Searches the `poolList` collection for the pool using its address.
2. **Result Handling:**
   - Returns `True` and pool details if found.
   - Returns `False` and a message if not found or if an error occurs.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if the pool is found, otherwise `False`. `message` contains the result or error details.

**Example Usage:**

```python
found, message = find_pool("pool123")
# Result: True or False, message with details
```

---

### `get_validator_percentage`

**Purpose:** Retrieve the percentage of a validator by their address.

**Parameters:**

- `validator_address`: The address of the validator.

**Process:**

1. **Database Query:** Searches the `validatorsList` collection for the validator using its address.
2. **Percentage Validation:** Checks if the validator's percentage is valid (≥1).
   - Returns `True` and the percentage if valid.
   - Returns `False` and a message if not valid or if an error occurs.

**Returns:**

- A tuple `(success, result)`. `success` is `True` if the validator is found with a valid percentage, otherwise `False`. `result` contains the percentage or error details.

**Example Usage:**

```python
success, percentage = get_validator_percentage("validator123")
# Result: True or False, percentage or message
```

---

### `set_pool_score`

**Purpose:** Update the score of a pool based on the validator's percentage.

**Parameters:**

- `pool_address`: The address of the pool.
- `validator_address`: The address of the validator.

**Process:**

1. **Check Pool Existence:** Calls `find_pool` to check if the pool exists.
2. **Get Validator Percentage:** Calls `get_validator_percentage` to retrieve the validator's percentage.
3. **Score Calculation:** Calculates the score increment based on the validator's percentage.
4. **Score Update:** Updates the pool's score in the `minerPool` collection, ensuring it does not exceed `MAX_SCORE`.
5. **Result Handling:**
   - Returns `True` and the updated score if successful.
   - Returns `False` and a message if not successful or if an error occurs.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if the score is updated, otherwise `False`. `message` contains the updated score or error details.

**Objective:** Increment the pool score based on the validator's percentage, ensuring the increment is bounded and does not exceed a maximum score.

- **Inputs:**

  - `percentage`: Validator's percentage.
  - `SCORE_INCREMENT_MAX`: Maximum allowed increment, fixed at 20.
  - `MAX_SCORE`: Maximum allowed score, fixed at 100.

- **Formulas:**

  1. **Calculate Score Increment:**

     <img src="https://latex.codecogs.com/svg.image?{\color{Blue}\large&space;&space;scoreIncrement=\sqsubset\left(percentage/100\right)\ast&space;scoreIncrementMax\sqsupset&space;}" alt="Calculate Score Increment"/>

  2. **Ensure Minimum Increment:**

     <img src="https://latex.codecogs.com/svg.image?{\color{Blue}\Large&space;\text{score\_increment}=\max(\text{score\_increment},1)}" alt="Ensure Minimum Increment">

  3. **Update Score:**

     <img src="https://latex.codecogs.com/svg.image?{\color{Blue}\Large&space;\text{new\_score}=\min(\text{MAX\_SCORE},\text{current\_score}+\text{score\_increment})}" alt="Update Score">

**Example Usage:**

```python
success, message = set_pool_score("pool123", "validator123")
# Result: True or False, message with details
```

---

### `set_validator_score`

**Purpose:** Set the score of a validator to 1.

**Parameters:**

- `validator_address`: The address of the validator.

**Process:**

1. **Check Validator Existence:** Searches the `validatorsList` collection for the validator using their address.
2. **Score Update:** Updates the validator's score to 1 in the database.
3. **Result Handling:**
   - Returns `True` if successful.
   - Returns `False` and a message if not successful or if an error occurs.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if the score is updated, otherwise `False`. `message` contains details of the update or error.

**Objective:** Set the validator's score to a fixed value of 1.

- **Inputs:**

  - Fixed score value: 1.

- **Formula:**

  <img src="https://latex.codecogs.com/svg.image?{\color{Blue}\Large&space;\text{new\_score}=1}" alt="New score">

**Example Usage:**

```python
success, message = set_validator_score("validator123")
# Result: True or False, message with details
```

---

### `decay_pool_score`

**Purpose:** Decay the score of all pools by 10%.

**Process:**

1. **Retrieve Pools:** Fetches all entries from the `minerPool` collection.
2. **Score Decay:** Reduces each pool's score by 10%, ensuring it does not drop below 0.
3. **Score Update:** Updates the decayed scores in the database.
4. **Logging:** Logs the score decay operation for each pool.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if the scores are updated, otherwise `False`. `message` contains details of the operation or error.

**Objective:** Decay the score of each pool by 10%, ensuring the score does not drop below 0.

- **Inputs:**

  - `current_score`: Current score of the pool.

- **Formulas:**

  1. **Calculate Score Decrement:**

     <img src="https://latex.codecogs.com/svg.image?{\color{Blue}\Large&space;\text{score\_decrement}=\left\lceil0.10\times\text{current\_score}\right\rceil}" alt="score_decrement">

  2. **Update Score:**

    <img src="https://latex.codecogs.com/svg.image?{\color{Blue}\Large&space;\text{new\_score}=\max(\text{current\_score}-\text{score\_decrement},0)}" alt="new_score">

**Example Usage:**

```python
success, message = decay_pool_score()
# Result: True or False, message with details
```

---

### `decay_validator_score`

**Purpose:** Reset the score of all validators to 0.

**Process:**

1. **Retrieve Validators:** Fetches all entries from the `validatorsList` collection.
2. **Score Reset:** Sets each validator's score to 0.
3. **Score Update:** Updates the reset scores in the database.
4. **Logging:** Logs the score reset operation for each validator.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if the scores are updated, otherwise `False`. `message` contains details of the operation or error.

**Objective:** Set the validator's score to 0.

- **Inputs:**

  - Fixed score value: 0.

- **Formula:**

  <img src="https://latex.codecogs.com/svg.image?{\color{Blue}\Large&space;\text{new\_score}=0}" alt="new score">

**Example Usage:**

```python
success, message = decay_validator_score()
# Result: True or False, message with details
```

---

### `update_scores`

**Purpose:** Update both pool and validator scores.

**Parameters:**

- `pool_address`: The address of the pool.
- `validator_address`: The address of the validator.

**Process:**

1. **Update Pool Score:** Calls `set_pool_score` to update the pool's score.
2. **Update Validator Score:** Calls `set_validator_score` to update the validator's score.
3. **Result Handling:**
   - Returns `True` if both updates are successful.
   - Returns `False` and a message if any update fails.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if both scores are updated, otherwise `False`. `message` contains details of the operation or error.

**Example Usage:**

```python
success, message = update_scores("pool123", "validator123")
# Result: True or False, message with details
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
   - Checks for relevant transactions (type "REGULAR" and addresses matching the miner pool wallet).
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

**Purpose:** Process block rewards by analyzing block data and distributing the rewards.

**Process:**

1. **Analyze Block Rewards:** Calls `analyze_block_rewards` to get the reward percentages and block range.
   - If `None` is returned, logs a message and skips reward processing.
2. **Distribute Rewards:** Calls the emission functions to distribute the rewards:
   - `pool_emission` for pool rewards.
   - `validator_emission` for validator rewards.
   - `iNode_emission` for iNode fees.
3. **Logging:** Logs the reward amounts for pools, validators, and iNode fees.
4. **Error Handling:** Logs errors if any exceptions occur during the process.

**Returns:**

- `None`

**Example Usage:**

```python
process_block_rewards()
# Result: None
```

---

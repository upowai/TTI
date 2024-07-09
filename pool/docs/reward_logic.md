## Reward_logic Documentation

## (`miner_reward.py`) Documentation

### `update_miner_balances`

**Purpose:** Update the balances of miners based on their scores and reset their scores.

**Parameters:**

- `amount`: The total reward amount to be distributed among miners.
- `block_range`: The range of blocks being processed, used for logging and tracking.
- `batch_size`: (Optional) The number of miners to process in each batch. Default is 1000.

**Process:**

1. **Convert Amount to Decimal:** Converts the provided `amount` to a `Decimal` for precise calculations.
2. **Initialize Variables:** Initializes a dictionary `miner_updates` to store update details and `total_score` to accumulate the total score of all miners.
3. **Fetch Miners with Positive Scores:** Queries the `userStats` collection to find miners with scores greater than zero.
4. **Calculate Total Score:** Iterates over the fetched miners to calculate the `total_score` and store miner data in a list `filtered_miners`.
   - Logs and exits if no miners have a positive score.
5. **Process Miners in Batches:** Iterates over `filtered_miners` in batches of size `batch_size` to distribute the reward amount proportionally based on their scores.
   - For each miner in the batch:
     - Calculates the miner's share of the reward.
     - Updates the miner's balance in the database.
     - Stores the update details in `miner_updates`.
6. **Convert Decimal to Float:** Converts all `Decimal` values in `miner_updates` to `float` using the `convert_decimal_to_float` function.
7. **Store Updates in Database:** Calls `store_in_db` to store the update details in the database.
8. **Logging:** Logs the successful update of balances and reset of scores.
9. **Error Handling:** Logs any exceptions that occur during the process.

**Returns:** None

**Example Usage:**

```python
update_miner_balances(1000, "1000-1010")
# Result: None, updates miner balances and resets scores
```

---

### Supporting Functions

#### `convert_decimal_to_float`

**Purpose:** Recursively convert all `Decimal` values in a data structure to `float`.

**Parameters:**

- `data`: The data structure (dict, list, or value) to be converted.

**Process:**

1. **Check Data Type:** Checks if the data is a dictionary, list, or `Decimal`.
2. **Recursive Conversion:** Recursively converts `Decimal` values to `float` in dictionaries and lists.
3. **Return Converted Data:** Returns the converted data structure.

**Returns:** The data structure with all `Decimal` values converted to `float`.

**Example Usage:**

```python
converted_data = convert_decimal_to_float({"amount": Decimal("10.5")})
# Result: {"amount": 10.5}
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

**Purpose:** Validate that the total of pool fee, miner reward percentages equals 100%.

**Process:**

1. **Retrieve Percentages:** Fetches the percentage values for pool fee, miner rewards from the `base` configuration.
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

**Purpose:** Calculate the distribution of a total amount based on predefined percentages for pool fees and miner rewards.

**Parameters:**

- `total_amount`: The total amount (as a `Decimal` or convertible to `Decimal`) to be distributed.

**Process:**

1. **Retrieve Percentages:** Fetches the percentage values for pool fees, and miner rewards from the `base` configuration.
2. **Convert to Decimal:** Converts the string percentage values to `Decimal` after removing the '%' sign.
3. **Total Validation:** Validates that the sum of the percentages equals 100%.
4. **Calculate Shares:** Divides the `total_amount` into portions based on the percentages:
   - Fee
   - Miner reward
5. **Round Shares:** Rounds each portion using `round_up_decimal_new`.

**Returns:**

- A dictionary with the keys `"18%"`, `"82%"`, representing the fee, miner reward portions respectively.
- `False` if the total percentage does not equal 100%.

**Example Usage:**

```python
shares = calculate_percentages(Decimal("1000"))
# Result: {'18%': Decimal('18.00000000'), '82%': Decimal('82.00000000')}
```

---

### `update_pool_reward`

**Purpose:** Update the reward amount for the pool owner.

**Parameters:**

- `amount`: The amount to be added to the pool owner's current balance.

**Process:**

1. **Convert Amount to Decimal:** Converts the provided `amount` to a `Decimal` for precise calculations.
2. **Fetch Pool Owner Data:** Queries the `entityOwners` collection to find the document with `_id` as `"entityOwners"`.
   - If the document exists, retrieves the current amount and wallet address.
   - If the document does not exist, initializes the current amount to `0.0` and uses the default wallet address from the `base` configuration.
3. **Calculate New Amount:** Adds the provided amount to the current amount and rounds the result using `round_up_decimal_new`.
4. **Get Current Time:** Retrieves the current UTC time in ISO format.
5. **Update Database:** Updates the `entityOwners` document in the database with the new amount, current time, and wallet address. Uses `upsert=True` to create the document if it does not exist.
6. **Error Handling:** Logs any exceptions that occur during the process.

**Returns:** None

**Example Usage:**

```python
update_pool_reward(1000)
# Result: None, updates pool owner's reward amount
```

---

## (`process_blocks.py` Documentation

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
2. **Distribute Rewards:** Calls the update functions to distribute the rewards:
   - `update_miner_balances` for miner rewards.
   - `update_pool_reward` for pool owner rewards.
3. **Logging:** Logs the reward amounts for miners and pool owners.
4. **Error Handling:** Logs errors if any exceptions occur during the process.

**Returns:** None

**Example Usage:**

```python
process_block_rewards()
# Result: None
```

---

### `calculate_speed_score`

**Purpose:** Calculate the speed score based on the task completion time.

**Parameters:**

- `task_completion_time_utc`: The UTC time when the task was completed, in ISO format.

**Process:**

1. **Convert Time String:** Converts the input time string to a `datetime` object.
2. **Calculate Time Difference:** Computes the time difference between the current UTC time and the task completion time in seconds.
3. **Score Calculation:** Determines the score based on the time difference:
   - Score is 10 if the time difference is 30 seconds or less.
   - Score decreases incrementally for longer time differences, with a minimum score of 1.
4. **Error Handling:** Logs and returns a score of 0 if an exception occurs.

**Returns:** The calculated score (integer).

**Example Usage:**

```python
score = calculate_speed_score("2024-06-24T12:34:56.789")
# Result: Integer score between 1 and 10
```

---

### `upsert_user_info`

**Purpose:** Upsert user information in the database.

**Parameters:**

- `wallet_address`: The wallet address of the user.
- `score`: (Optional) The score to be added to the user's current score.

**Process:**

1. **Find User:** Searches for the user by wallet address in the `userStats` collection.
2. **Update Existing User:** If the user exists, updates their last active time and increments their score (if provided).
3. **Create New User:** If the user does not exist, creates a new user document with default values.
4. **Error Handling:** Returns a message indicating the result of the operation or an error message if an exception occurs.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if the operation is successful, otherwise `False`. `message` contains details of the operation or error.

**Example Usage:**

```python
success, message = upsert_user_info("wallet123", 5)
# Result: (True, "User updated with wallet_address: wallet123") or (False, "Error message")
```

---

### `add_processed_validator`

**Purpose:** Add a validator to the list of processed validators for a task.

**Parameters:**

- `val_id`: The ID of the validation task.
- `validator_address`: The address of the validator.

**Process:**

1. **Find Task:** Searches for the task by `val_id` in the `ValidationTask` collection.
2. **Check Validator List:** Checks if the validator is already in the list of processed validators.
3. **Update Validator List:** If the validator is not in the list, adds them and updates the task document.
4. **Error Handling:** Logs and returns `False` if an exception occurs.

**Returns:**

- `True` if the validator is successfully added.
- `False` if the validator is already in the list or if an error occurs.

**Example Usage:**

```python
success = add_processed_validator("val123", "validator123")
# Result: True or False
```

---

### `is_task_valid`

**Purpose:** Check if a task is valid based on its creation time.

**Parameters:**

- `val_id`: The ID of the validation task.

**Process:**

1. **Find Task:** Searches for the task by `val_id` in the `ValidationTaskHistory` collection.
2. **Parse Creation Time:** Converts the task's `createdAt` field to a `datetime` object.
3. **Check Time Difference:** Determines if the task was created within the last hour.
4. **Error Handling:** Logs and returns `False` if an exception occurs.

**Returns:**

- `True` if the task is valid.
- `False` if the task is not found, if it was created more than an hour ago, or if an error occurs.

**Example Usage:**

```python
is_valid = is_task_valid("val123")
# Result: True or False
```

---

### `miner_eligibility`

**Purpose:** Check if a miner is eligible based on their wallet address.

**Parameters:**

- `wallet_address`: The wallet address of the miner.

**Process:**

1. **Find User:** Searches for the user by wallet address in the `userStats` collection.
2. **Check Eligibility:** Determines if the user is eligible based on their `np` (non-performing) field.
   - The user is ineligible if `np` is greater than 45.
3. **Error Handling:** Logs and returns `False` if an exception occurs.

**Returns:**

- `True` if the user is eligible.
- `False` if the user is ineligible or if an error occurs.

**Example Usage:**

```python
is_eligible = miner_eligibility("wallet123")
# Result: True or False
```

---

### `task_validation_output`

**Purpose:** Update the TP (True Positive) and NP (False Negative) values for a user based on their wallet address.

**Parameters:**

- `wallet_address`: The wallet address of the user.
- `tp`: (Optional) The value to increment the TP field by.
- `np`: (Optional) The value to increment the NP field by.

**Process:**

1. **Find User:** Searches for the user by wallet address in the `userStats` collection.
   - Returns `False` and a message if the user is not found.
2. **Prepare Update Document:** Prepares an update document to increment TP and/or NP fields.
   - Returns `False` and a message if there are no updates to perform.
3. **Update User Stats:** Updates the user's statistics in the database.
4. **Error Handling:** Returns a message indicating the result of the operation or an error message if an exception occurs.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if the operation is successful, otherwise `False`. `message` contains details of the operation or error.

**Example Usage:**

```python
success, message = task_validation_output("wallet123", tp=5, np=2)
# Result: (True, "User validated with wallet_address: wallet123") or (False, "Error message")
```

---

### `update_validation_task`

**Purpose:** Update the status and output of a specific task within a validation task array.

**Parameters:**

- `task_id`: The ID of the task to update.
- `output`: The output of the task.
- `wallet_address`: The wallet address associated with the task.

**Process:**

1. **Find Task:** Searches for the validation task by `task_id` in the `ValidationTask` collection.
   - Returns `False` and a message if the task is not found.
2. **Update Task:** Updates the specific task within the validation task array.
3. **Check Completion:** Checks if all tasks in the array are completed.
   - Updates the condition to "dispatch" if all tasks are completed.
4. **Error Handling:** Returns a message indicating the result of the operation or an error message if an exception occurs.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if the operation is successful, otherwise `False`. `message` contains details of the operation or error.

**Example Usage:**

```python
success, message = update_validation_task("task123", "output", "wallet123")
# Result: (True, "Task updated successfully") or (False, "Error message")
```

---

### `generate_validation_task`

**Purpose:** Generate a new validation task with multiple subtasks and insert them into the database.

**Process:**

1. **Check Collection:** Checks if the `ValidationTask` collection is empty.
   - Skips insertion if the collection is not empty.
2. **Generate Task Data:** Generates random text for the task and creates an array of subtasks.
3. **Create Validation Task Document:** Creates a validation task document with the generated subtasks and inserts it into the `ValidationTask` collection.
4. **Insert Subtasks:** Inserts each subtask into the `AiTask` collection.
5. **Error Handling:** Logs and returns `False` if an exception occurs.

**Returns:**

- `True` if the validation task is successfully inserted.
- `False` if the collection is not empty or if an error occurs.

**Example Usage:**

```python
success = await generate_validation_task()
# Result: True or False
```

---

### `select_task_for_validation`

**Purpose:** Select a task for validation based on its condition and time since creation.

**Process:**

1. **Find Task:** Searches for the first task in the `ValidationTask` collection.
   - Returns an error message if no tasks are found.
2. **Check Time Difference:** Compares the current time with the task's creation time.
   - Deletes the task if it has been pending or dispatched for more than the configured timer duration.
3. **Check Condition:** Returns an error message if the task condition is not "dispatch".
4. **Return Task Details:** Returns the task details as JSON if all checks pass.
5. **Error Handling:** Returns an error message if an exception occurs.

**Returns:**

- A tuple `(success, message)`. `success` is `True` if a suitable task is found, otherwise `False`. `message` contains task details or an error message.

**Example Usage:**

```python
success, message = await select_task_for_validation()
# Result: (True, "task details in JSON") or (False, "Error message")
```

---

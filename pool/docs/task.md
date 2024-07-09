## Task Documentation

## (`task.py`) Documentation

### `generate_task`

**Purpose:** Generate a new task with random text and insert it into the `AiTask` collection.

**Process:**

1. **Generate Task Data:** Generates random text for the task, a unique ID, a retrieve ID, and sets initial values for other fields such as status and type.
2. **Insert Task Document:** Inserts the generated task document into the `AiTask` collection.
3. **Error Handling:** Logs any exceptions that occur during the process.

**Returns:**

- `True` if the task is successfully inserted.
- `False` if the insertion fails.
- `False` if an error occurs.

**Example Usage:**

```python
success = await generate_task()
# Result: True or False
```

---

### `generate_automatic_task`

**Purpose:** Generate a new automatic task with random text for a given wallet address and insert it into the `AiTask` collection.

**Parameters:**

- `walletAddress`: The wallet address to associate with the task.

**Process:**

1. **Generate Task Data:** Generates random text for the task, a unique ID, a retrieve ID, and sets initial values for other fields such as status and type.
2. **Insert Task Document:** Inserts the generated task document into the `AiTask` collection.
3. **Return Task Data:** Returns the task data including ID, task text, seed, and message type.
4. **Error Handling:** Logs any exceptions that occur during the process.

**Returns:**

- A dictionary with task details if the task is successfully inserted.
- `None` if the insertion fails or an error occurs.

**Example Usage:**

```python
task_data = await generate_automatic_task("wallet123")
# Result: Dictionary with task details or None
```

---

### `update_task`

**Purpose:** Update a task with a given document ID and wallet address.

**Parameters:**

- `document_id`: The ID of the task document to update.
- `wallet_address`: The wallet address to associate with the task.

**Process:**

1. **Get Current Time:** Retrieves the current UTC time in ISO format.
2. **Update Task Document:** Updates the task document in the `AiTask` collection with the new wallet address, current time, and status set to "sent".
3. **Return Update Status:** Returns whether the update was acknowledged by MongoDB.

**Returns:**

- `True` if the update is acknowledged.
- `False` if the update is not acknowledged.

**Example Usage:**

```python
success = await update_task("task123", "wallet123")
# Result: True or False
```

---

### `find_task`

**Purpose:** Find a suitable task for a given wallet address or generate a new automatic task if no suitable task is found.

**Parameters:**

- `wallet_address`: The wallet address to find a task for.

**Process:**

1. **Check for Sent Tasks:** Checks if the wallet address has any "sent" tasks that are not completed.
2. **Fetch All Tasks:** Retrieves all tasks sorted by time and converts them to a list.
3. **Generate New Task:** If no tasks are found, generates a new automatic task.
4. **Sort by Priority:** Sorts tasks by priority and checks each task for suitability based on status and time.
5. **Update and Return Task:** Updates the suitable task with the wallet address and returns its details.
6. **Error Handling:** Logs any exceptions that occur during the process.

**Returns:**

- A tuple `(task_id, task_details)` if a suitable task is found or generated.
- `(None, None)` if no suitable task is found or an error occurs.

**Example Usage:**

```python
task_id, task_details = await find_task("wallet123")
# Result: (task_id, task_details) or (None, None)
```

---

### `calculate_speed_score`

**Purpose:** Calculate a speed score based on the time taken to complete a task.

**Parameters:**

- `task_completion_time_utc`: The UTC time string indicating when the task was completed. The format should be `"%Y-%m-%dT%H:%M:%S.%f"`.

**Process:**

1. **Convert Time String to Datetime Object:**
   - Parses the input UTC time string to a datetime object.
2. **Get Current UTC Time:**

   - Retrieves the current time in UTC.

3. **Calculate Time Difference:**

   - Computes the difference between the current time and the task completion time in seconds.

4. **Calculate Score:**
   - Assigns a score based on the time difference:
     - Full score (10) if the task is completed within 6 seconds.
     - The score decreases by 1 for every additional 5 seconds beyond the initial 6 seconds.
     - The minimum score is 1.
5. **Error Handling:**
   - Logs an error message if an exception occurs and returns a score of 0.

**Returns:**

- An integer score between 1 and 10 based on the task completion time.
- Returns 0 if an error occurs during the process.

**Example Usage:**

```python
score = calculate_speed_score("2024-07-03T12:34:56.789")
# Result: score (an integer between 1 and 10)
```

---

### `store_response`

**Purpose:** Store a response for a given task in the `ResponseTask` collection.

**Parameters:**

- `task_id`: The ID of the task associated with the response.
- `wallet_address`: The wallet address associated with the response.
- `output`: The output of the task.
- `retrieve_id`: The retrieve ID for the response.

**Process:**

1. **Calculate Expiration Time:** Sets an expiration time for the response document.
2. **Create Response Document:** Creates a response document with the given details.
3. **Insert Response Document:** Inserts the response document into the `ResponseTask` collection.
4. **Return Insertion Status:** Returns whether the insertion was acknowledged by MongoDB.
5. **Error Handling:** Logs any exceptions that occur during the process.

**Returns:**

- A tuple `(success, message)` indicating the success status and a message.

**Example Usage:**

```python
success, message = await store_response("task123", "wallet123", "output", "retrieve123")
# Result: (True, "Response stored successfully") or (False, "Error message")
```

---

### `handle_miner_response`

**Purpose:** Handle a response from a miner for a given task.

**Parameters:**

- `task_id`: The ID of the task to handle the response for.
- `wallet_address`: The wallet address of the miner.
- `output`: The output of the task provided by the miner.

**Process:**

1. **Find Task:** Retrieves the task from the `AiTask` collection by its ID.
2. **Validate Task:** Checks if the task exists, if the wallet address matches, and if the task status is "sent".
3. **Update Task Status:** Updates the task status to "completed" and adds the output.
4. **Store Response:** Calls `store_response` to store the response in the `ResponseTask` collection.
5. **Update User Info:** Updates the user information with a calculated score.
6. **Return Response Status:** Returns whether the task handling and response storage were successful.
7. **Error Handling:** Logs any exceptions that occur during the process.

**Returns:**

- A tuple `(success, message)` indicating the success status and a message.

**Example Usage:**

```python
success, message = await handle_miner_response("task123", "wallet123", "output")
# Result: (True, "Task Accepted and Response Stored") or (False, "Error message")
```

---

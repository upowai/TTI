## Task Documentation

## (`task.py`) Documentation

### `handle_pool_response`

**Purpose:** Handle responses from pools and insert validation tasks into the database.

**Parameters:**

- `val_id`: The validation task ID.
- `task_info`: A list of task information.
- `pool_wallet`: The wallet address of the pool.
- `pool_ip`: The IP address of the pool.
- `pool_port`: The port of the pool.

**Process:**

1. **Check Existing Document:** Checks if a document with the provided `val_id` already exists in the `storeTasks` collection.
2. **Prepare Task Information:** Formats the `task_info` to include additional fields such as `task`, `wallet_address`, `time`, `retrieve_id`, `status`, and `type`.
3. **Insert Document:** Inserts the formatted task information into the `storeTasks` collection.
4. **Error Handling:** Returns error messages if any exceptions occur during the process.

**Returns:**

- A tuple `(success, message)` indicating whether the operation was successful and a corresponding message.

**Example Usage:**

```python
success, message = await handle_pool_response("val123", task_info, "wallet123", "127.0.0.1", 8000)
# Result: (True, "Document created with val_id: val123.") or (False, "Error message")
```

---

### `validate_tasks`

**Purpose:** Validate tasks by moving them from `storeTasks` to `poolTasks` and `iNodeTask` collections.

**Process:**

1. **Find Task:** Finds the first document in the `storeTasks` collection.
2. **Extract Information:** Extracts necessary information such as `val_id`, `pool_wallet`, `pool_ip`, and `pool_port`.
3. **Get Unique Wallets:** Identifies unique wallet addresses from the task information.
4. **Prepare and Insert Document:** Prepares a document for the `poolTasks` collection and inserts it.
5. **Delete Store Task:** Deletes the processed task from the `storeTasks` collection.
6. **Prepare and Insert iNode Task:** Prepares and inserts a document into the `iNodeTask` collection.
7. **Error Handling:** Returns error messages if any exceptions occur during the process.

**Returns:**

- A tuple `(success, message)` indicating whether the operation was successful and a corresponding message.

**Example Usage:**

```python
success, message = validate_tasks()
# Result: (True, "Document successfully moved...") or (False, "Error message")
```

---

### `find_inode_task`

**Purpose:** Find the first task in the `iNodeTask` collection.

**Process:**

1. **Find Task:** Searches for the first document in the `iNodeTask` collection.
2. **Error Handling:** Returns error messages if any exceptions occur during the process.

**Returns:**

- A tuple `(success, document)` where `document` contains the found task if successful, or an error message if not.

**Example Usage:**

```python
success, document = find_inode_task()
# Result: (True, document) or (False, "Error message")
```

---

### `find_pool_task`

**Purpose:** Find the first task in the `poolTasks` collection.

**Process:**

1. **Find Task:** Searches for the first document in the `poolTasks` collection.
2. **Error Handling:** Returns error messages if any exceptions occur during the process.

**Returns:**

- A tuple `(success, document)` where `document` contains the found task if successful, or an error message if not.

**Example Usage:**

```python
success, document = find_pool_task()
# Result: (True, document) or (False, "Error message")
```

---

### `delete_inode_task`

**Purpose:** Delete a task from the `iNodeTask` collection based on `val_id`.

**Parameters:**

- `val_id`: The validation task ID to delete.

**Process:**

1. **Define Query:** Defines the query based on `val_id`.
2. **Delete Task:** Finds and deletes the document from the `iNodeTask` collection.
3. **Error Handling:** Returns error messages if any exceptions occur during the process.

**Returns:**

- A tuple `(success, message)` indicating whether the operation was successful and a corresponding message.

**Example Usage:**

```python
success, message = delete_inode_task("val123")
# Result: (True, "Task with val_id 'val123' deleted successfully.") or (False, "Error message")
```

---

### `delete_pool_task`

**Purpose:** Delete a task from the `poolTasks` collection based on `val_id`.

**Parameters:**

- `val_id`: The validation task ID to delete.

**Process:**

1. **Define Query:** Defines the query based on `val_id`.
2. **Delete Task:** Finds and deletes the document from the `poolTasks` collection.
3. **Error Handling:** Returns error messages if any exceptions occur during the process.

**Returns:**

- A tuple `(success, message)` indicating whether the operation was successful and a corresponding message.

**Example Usage:**

```python
success, message = delete_pool_task("val123")
# Result: (True, "Task with val_id 'val123' deleted successfully.") or (False, "Error message")
```

---

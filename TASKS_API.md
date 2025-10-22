# Tasks API Documentation

## Task Endpoints

### 1. Create Message Task

**POST** `/tasks/`

Creates an asynchronous task to insert a message into the database.

**Request Body:**

```json
{
  "content": "My message"
}
```

**Response (202 Accepted):**

```json
{
  "task_id": "80e7794a-bee8-4b21-9f89-7464719214f5",
  "status": "PENDING",
  "message": "Task enqueued successfully"
}
```

**Example curl:**

```bash
curl -X POST http://localhost:8060/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello World"}'
```

---

### 2. Create Slow Task (For Testing)

**POST** `/tasks/slow`

Creates a task that takes several seconds to complete. Useful for testing active task listings.

**Query Parameters:**

- `duration` (optional): Duration in seconds (default: 10)

**Response (202 Accepted):**

```json
{
  "task_id": "8d3b9b88-e8ce-4ce2-8d66-dd0623128d2d",
  "status": "PENDING",
  "message": "Slow task enqueued for 10 seconds"
}
```

**Example curl:**

```bash
curl -X POST "http://localhost:8060/tasks/slow?duration=30"
```

---

### 3. List All Active Tasks

**GET** `/tasks/`

Lists all tasks that are currently active, scheduled, or reserved in Celery.

**Response (200 OK):**

```json
{
  "tasks": [
    {
      "task_id": "80e7794a-bee8-4b21-9f89-7464719214f5",
      "status": "ACTIVE"
    },
    {
      "task_id": "8d3b9b88-e8ce-4ce2-8d66-dd0623128d2d",
      "status": "SCHEDULED"
    }
  ],
  "total": 2
}
```

**Possible statuses:**

- `ACTIVE`: Task currently being executed
- `SCHEDULED`: Task scheduled for future execution
- `RESERVED`: Task in queue but not yet active

**Example curl:**

```bash
curl http://localhost:8060/tasks/
```

**⚠️ Important:**

- This endpoint lists only **pending/active** tasks
- Completed tasks (SUCCESS/FAILURE) don't appear because the app uses RPC backend
- For completed tasks, check the `/messages/` endpoint to see created records
- To track a specific task, use `GET /tasks/{task_id}` right after creating it

---

### 4. Query Task Status

**GET** `/tasks/{task_id}`

Queries the status and result of a specific task by ID.

**Response (200 OK):**

**Pending task:**

```json
{
  "task_id": "80e7794a-bee8-4b21-9f89-7464719214f5",
  "status": "PENDING",
  "result": null
}
```

**Running task:**

```json
{
  "task_id": "80e7794a-bee8-4b21-9f89-7464719214f5",
  "status": "STARTED",
  "result": null
}
```

**Successfully completed task:**

```json
{
  "task_id": "80e7794a-bee8-4b21-9f89-7464719214f5",
  "status": "SUCCESS",
  "result": {
    "id": 123,
    "content": "Hello World",
    "created_at": "2025-10-16T14:30:00"
  }
}
```

**Failed task:**

```json
{
  "task_id": "80e7794a-bee8-4b21-9f89-7464719214f5",
  "status": "FAILURE",
  "result": {
    "error": "Database connection failed"
  }
}
```

**Example curl:**

```bash
curl http://localhost:8060/tasks/80e7794a-bee8-4b21-9f89-7464719214f5
```

---

## Complete Flow Example

### 1. Create a slow task for testing

```bash
# Create 30-second task
curl -X POST "http://localhost:8060/tasks/slow?duration=30"
```

**Response:**

```json
{
  "task_id": "abc-123",
  "status": "PENDING",
  "message": "Slow task enqueued for 30 seconds"
}
```

### 2. List active tasks (execute quickly)

```bash
curl http://localhost:8060/tasks/
```

**Response:**

```json
{
  "tasks": [
    {
      "task_id": "abc-123",
      "status": "ACTIVE"
    }
  ],
  "total": 1
}
```

### 3. Check specific status

```bash
curl http://localhost:8060/tasks/abc-123
```

**Response (while running):**

```json
{
  "task_id": "abc-123",
  "status": "STARTED",
  "result": null
}
```

### 4. Wait 30 seconds and check again

```bash
# After 30 seconds
curl http://localhost:8060/tasks/abc-123
```

**Response (after completion):**

```json
{
  "task_id": "abc-123",
  "status": "SUCCESS",
  "result": {
    "message": "Task completed after 30 seconds"
  }
}
```

### 5. Verify it no longer appears in active list

```bash
curl http://localhost:8060/tasks/
```

**Response:**

```json
{
  "tasks": [],
  "total": 0
}
```

---

## Comparison: RPC Backend vs Redis Backend

**Current (RPC Backend):**

- ✅ Simple, no additional dependency
- ✅ Good for development
- ❌ Doesn't persist results
- ❌ Can't list completed tasks

**With Redis Backend:**

- ✅ Persists results
- ✅ Allows querying history
- ✅ Allows listing all tasks
- ❌ Requires additional configuration
- ❌ One more service to manage

---

## Testing in Swagger Interface

Access: <http://localhost:8060/docs>

1. Open the **Tasks** section
2. Try the endpoints:
   - POST `/tasks/slow` - Create test task
   - GET `/tasks/` - List active tasks
   - GET `/tasks/{task_id}` - View specific status

---

## Usage Tips

1. **For quick debugging**: Use `/tasks/slow?duration=5` to create tasks that last 5 seconds

2. **To monitor tasks**:

   ```bash
   # In one terminal, create task
   curl -X POST "http://localhost:8060/tasks/slow?duration=20"
   
   # In another terminal, monitor
   watch -n 1 'curl -s http://localhost:8060/tasks/ | python3 -m json.tool'
   ```

3. **To see created messages**:

   ```bash
   curl http://localhost:8060/messages/
   ```

4. **To clear old messages** (if needed):
   - Access RabbitMQ Management: <http://localhost:15672>
   - Or check logs: `docker compose logs worker`

---

## Understanding Task States

### Celery Task Lifecycle

```text
PENDING → STARTED → SUCCESS
                  ↘ FAILURE
                  ↘ RETRY
```

### State Descriptions

- **PENDING**: Task waiting to be executed
- **STARTED**: Task is currently being processed by a worker
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task failed with an error
- **RETRY**: Task is being retried after a failure

### Visibility with RPC Backend

With the current RPC backend configuration:

✅ **Visible in `/tasks/` endpoint:**

- PENDING tasks (in queue)
- STARTED tasks (being executed)
- Tasks in worker's active list

❌ **Not visible in `/tasks/` endpoint:**

- SUCCESS tasks (already completed and consumed)
- FAILURE tasks (already completed and consumed)
- Tasks older than a few minutes

💡 **Solution**: Use Flower (<http://localhost:5555>) for better task visibility!

---

## Real-World Example: Processing Flow

### Scenario: Creating Messages in Batch

```bash
# 1. Create multiple tasks
for i in {1..5}; do
  curl -X POST http://localhost:8060/tasks/ \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"Message $i\"}"
  sleep 0.5
done

# 2. Check active tasks
curl http://localhost:8060/tasks/ | python3 -m json.tool

# 3. Wait a moment for processing
sleep 2

# 4. Verify messages were created
curl http://localhost:8060/messages/ | python3 -m json.tool
```

### Expected Output

After step 2 (if tasks are fast, might be empty):

```json
{
  "tasks": [
    {"task_id": "...", "status": "ACTIVE"}
  ],
  "total": 1
}
```

After step 4:

```json
{
  "messages": [
    {
      "id": 1,
      "content": "Message 1",
      "created_at": "2025-10-16T10:00:00"
    },
    {
      "id": 2,
      "content": "Message 2",
      "created_at": "2025-10-16T10:00:01"
    },
    // ... etc
  ],
  "total": 5
}
```

---

## Advanced: Testing with Multiple Slow Tasks

### Create Multiple Tasks and Monitor

```bash
# Terminal 1: Create 10 slow tasks (20 seconds each)
for i in {1..10}; do
  curl -X POST "http://localhost:8060/tasks/slow?duration=20"
  echo " # Task $i created"
  sleep 1
done

# Terminal 2: Monitor active tasks every 2 seconds
watch -n 2 'curl -s http://localhost:8060/tasks/ | python3 -m json.tool'

# Terminal 3: Check Flower for better visualization
open http://localhost:5555/monitor
```

### What You'll See

- **API `/tasks/`**: Shows active/scheduled tasks as simple list
- **Flower Monitor**: Shows real-time execution with progress bars
- **Flower Tasks**: Shows complete history with details

---

## Troubleshooting

### Problem: Empty task list even when tasks are running

**Cause**: Tasks execute too fast (< 1 second)

**Solution**: Use slow tasks for testing:

```bash
curl -X POST "http://localhost:8060/tasks/slow?duration=30"
# Then quickly check:
curl http://localhost:8060/tasks/
```

### Problem: Can't find completed tasks

**Cause**: RPC backend doesn't persist results after consumption

**Solutions:**

1. **Use Flower** for visual monitoring:
   - <http://localhost:5555/tasks>

2. **Check created messages** (for message tasks):
   - `curl http://localhost:8060/messages/`

3. **Upgrade to Redis backend** (for production):

   ```yaml
   # docker-compose.yml
   services:
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
   
   # backend/.env
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   ```

### Problem: Task stuck in PENDING state

**Diagnosis:**

```bash
# Check if worker is running
docker compose ps worker

# Check worker logs
docker compose logs worker

# Check RabbitMQ queues
curl -u guest:guest http://localhost:15672/api/queues
```

**Common causes:**

- Worker is not running
- Worker crashed
- Wrong queue configuration
- Network issues

**Solution:**

```bash
# Restart worker
docker compose restart worker

# Or rebuild if code changed
docker compose up -d --build worker
```

---

## API Response Status Codes

| Code | Meaning | When |
|------|---------|------|
| **200 OK** | Success | GET requests successful |
| **202 Accepted** | Accepted | Task created and queued |
| **404 Not Found** | Not found | Invalid task_id or endpoint |
| **422 Unprocessable Entity** | Validation error | Invalid request body |
| **500 Internal Server Error** | Server error | Unexpected error occurred |

---

## Best Practices

### 1. Always Save Task IDs

When creating tasks, save the returned `task_id`:

```bash
TASK_ID=$(curl -X POST http://localhost:8060/tasks/slow?duration=20 | jq -r '.task_id')
echo "Created task: $TASK_ID"

# Later, check status
curl http://localhost:8060/tasks/$TASK_ID
```

### 2. Use Appropriate Task Types

- **Production**: Use `/tasks/` (message task) for real work
- **Testing**: Use `/tasks/slow` to simulate long-running tasks

### 3. Monitor with the Right Tool

- **Quick checks**: `/tasks/` endpoint
- **Deep debugging**: Flower UI
- **Production monitoring**: Flower + external monitoring (Prometheus, etc.)

### 4. Handle Task Failures

Always check task status:

```python
import requests
import time

# Create task
response = requests.post("http://localhost:8060/tasks/", json={"content": "Test"})
task_id = response.json()["task_id"]

# Poll for completion
max_wait = 30
interval = 1
elapsed = 0

while elapsed < max_wait:
    status_response = requests.get(f"http://localhost:8060/tasks/{task_id}")
    status = status_response.json()["status"]
    
    if status == "SUCCESS":
        print("Task completed successfully!")
        break
    elif status == "FAILURE":
        print("Task failed!")
        break
    
    time.sleep(interval)
    elapsed += interval
```

---

## Integration Examples

### Python Script

```python
import requests
import json

BASE_URL = "http://localhost:8060"

def create_message_task(content: str) -> dict:
    """Create a message task and return task info"""
    response = requests.post(
        f"{BASE_URL}/tasks/",
        json={"content": content}
    )
    return response.json()

def list_active_tasks() -> dict:
    """List all active tasks"""
    response = requests.get(f"{BASE_URL}/tasks/")
    return response.json()

def get_task_status(task_id: str) -> dict:
    """Get status of specific task"""
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    return response.json()

# Usage
if __name__ == "__main__":
    # Create task
    task = create_message_task("Hello from Python!")
    print(f"Created task: {task['task_id']}")
    
    # List active
    active = list_active_tasks()
    print(f"Active tasks: {active['total']}")
    
    # Check specific task
    status = get_task_status(task['task_id'])
    print(f"Task status: {status['status']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8060';

async function createMessageTask(content) {
  const response = await axios.post(`${BASE_URL}/tasks/`, {
    content: content
  });
  return response.data;
}

async function listActiveTasks() {
  const response = await axios.get(`${BASE_URL}/tasks/`);
  return response.data;
}

async function getTaskStatus(taskId) {
  const response = await axios.get(`${BASE_URL}/tasks/${taskId}`);
  return response.data;
}

// Usage
(async () => {
  // Create task
  const task = await createMessageTask('Hello from Node.js!');
  console.log(`Created task: ${task.task_id}`);
  
  // List active
  const active = await listActiveTasks();
  console.log(`Active tasks: ${active.total}`);
  
  // Check specific task
  const status = await getTaskStatus(task.task_id);
  console.log(`Task status: ${status.status}`);
})();
```

---

## Next Steps

### For Development

1. ✅ Use `/tasks/slow` to test monitoring
2. ✅ Use Flower for visual debugging
3. ✅ Check logs with `docker compose logs -f worker`

### For Production

1. ⚠️ Consider Redis backend for persistence
2. ⚠️ Add authentication to Flower
3. ⚠️ Set up external monitoring (Prometheus, Grafana)
4. ⚠️ Configure task timeouts and retries
5. ⚠️ Implement proper error handling

### Additional Features to Implement

- Task cancellation
- Task prioritization
- Scheduled/periodic tasks
- Task chaining
- Task groups/chords

---

**For more information:**

- See [FLOWER.md](./FLOWER.md) for Flower monitoring guide
- See [QUICK_ACCESS.md](./QUICK_ACCESS.md) for quick reference
- See [README.md](./README.md) for project overview

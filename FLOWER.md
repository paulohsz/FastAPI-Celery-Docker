# Flower - Celery Task Monitoring

## What is Flower?

**Flower** is a real-time monitoring tool for Celery. It provides a rich and interactive web interface to monitor and manage Celery workers and their tasks.

## Accessing Flower

After starting the containers, access Flower at:

🌸 **<http://localhost:5555>**

## Available Features

### 1. Main Dashboard

![Dashboard](real-time visualization)

- **Active workers**: Number of workers running
- **Processed tasks**: Total tasks executed
- **Success rate**: Percentage of successful tasks
- **Real-time graphs**: Activity visualization

### 2. Tasks

**URL**: <http://localhost:5555/tasks>

View all tasks with:

- **Task ID**: Unique task identifier
- **Task name**: E.g., `app.tasks.create_message_task`
- **State**: PENDING, STARTED, SUCCESS, FAILURE, RETRY
- **Arguments**: Parameters passed to the task
- **Result**: Task return value
- **Worker**: Which worker executed it
- **Runtime**: Execution time
- **Timestamp**: When it was executed

**Available filters:**

- By state (Success, Failure, etc.)
- By task name
- By worker
- By time interval

### 3. Workers

**URL**: <http://localhost:5555/workers>

Information about each worker:

- **Status**: Online/Offline
- **Active tasks**: How many tasks are being processed
- **Processed tasks**: Total completed tasks
- **Load average**: System load
- **Concurrency**: Number of processes/threads
- **Pool type**: prefork, eventlet, gevent, etc.

**Available actions:**

- Shutdown worker
- Restart worker
- Pool restart
- Pool grow/shrink

### 4. Monitor

**URL**: <http://localhost:5555/monitor>

Real-time monitoring with auto-refresh:

- Status of all active tasks
- Execution progress
- Elapsed time
- Updates every second

### 5. Broker (Queue)

**URL**: <http://localhost:5555/broker>

Information about RabbitMQ:

- **Active connections**: How many open connections
- **Queues**: List of all queues
- **Messages in queue**: How many tasks waiting
- **Message rate**: Messages per second

### 6. Configuration

**URL**: <http://localhost:5555/config>

View Celery configuration:

- Broker settings
- Result settings
- Time limits
- Serialization
- Routing

## Usage Examples

### 1. Monitor Tasks in Real-Time

1. Access <http://localhost:5555/monitor>
2. In another terminal, create several tasks:

   ```bash
   # Create 5 slow tasks
   for i in {1..5}; do
     curl -X POST "http://localhost:8060/tasks/slow?duration=10"
   done
   ```

3. Watch the tasks appearing and being processed in real-time in Flower

### 2. Check Success Rate

1. Access <http://localhost:5555/dashboard>
2. Observe the graphs:
   - Success rate
   - Failure rate
   - Throughput (tasks per second)

### 3. Debug Failed Tasks

1. Access <http://localhost:5555/tasks>
2. Filter by state: "FAILURE"
3. Click on the task to see:
   - Complete stack trace
   - Arguments that caused the failure
   - When it failed
   - Which worker executed it

### 4. View Specific Task History

1. Copy the `task_id` when creating a task
2. In Flower, access <http://localhost:5555/task/{task_id}>
3. See all details: states, timestamps, result

### 5. Manage Workers

1. Access <http://localhost:5555/workers>
2. To restart a worker, click "Restart"
3. To increase concurrency, use "Pool Grow"

## Comparison: Flower vs API `/tasks/`

| Feature | Flower | API `/tasks/` |
|---------|--------|---------------|
| **Active tasks** | ✅ Yes | ✅ Yes |
| **Complete history** | ✅ Yes (limited by backend) | ❌ No |
| **Graphical interface** | ✅ Yes | ❌ No (JSON only) |
| **Filters and search** | ✅ Advanced | ❌ No |
| **Statistics** | ✅ Graphs and metrics | ❌ No |
| **Worker control** | ✅ Shutdown, restart, etc. | ❌ No |
| **Real-time view** | ✅ Auto-refresh | ⚠️ Manual |
| **Programmatic access** | ⚠️ Via limited REST API | ✅ Yes |

## Flower REST API

Flower also offers a REST API for programmatic access:

### List Workers

```bash
curl http://localhost:5555/api/workers
```

### List Tasks

```bash
curl http://localhost:5555/api/tasks
```

### Task Information

```bash
curl http://localhost:5555/api/task/info/{task_id}
```

### Statistics

```bash
curl http://localhost:5555/api/workers/stats
```

## Advanced Configuration

### Basic Authentication

To add authentication, edit `docker-compose.yml`:

```yaml
flower:
  # ...
  command: celery -A app.celery_app flower --port=5555 --basic_auth=admin:password123
```

### Data Persistence

By default, Flower keeps data in memory. To persist:

```yaml
flower:
  # ...
  command: celery -A app.celery_app flower --port=5555 --persistent=True --db=/data/flower.db
  volumes:
    - ./backend:/app
    - flower_data:/data
```

And add the volume:

```yaml
volumes:
  postgres_data:
  rabbitmq_data:
  flower_data:
```

### URL Prefix

If you use a reverse proxy:

```yaml
flower:
  # ...
  command: celery -A app.celery_app flower --port=5555 --url_prefix=flower
```

Access at: <http://localhost:5555/flower>

## Troubleshooting

### Flower doesn't start

```bash
# View Flower logs
docker compose logs flower

# Check if container is running
docker compose ps flower
```

### I don't see tasks in Flower

1. **Check if worker is connected**:
   - Access <http://localhost:5555/workers>
   - Should show at least 1 worker

2. **Check the broker**:
   - Access <http://localhost:5555/broker>
   - Should show connection to RabbitMQ

3. **Create a test task**:

   ```bash
   curl -X POST "http://localhost:8060/tasks/slow?duration=5"
   ```

4. **Quickly access the monitor**:
   - <http://localhost:5555/monitor>

### Flower shows old data

- Restart the container:

  ```bash
  docker compose restart flower
  ```

- Or clear the state (if using persistence):

  ```bash
  docker compose down
  docker volume rm learning_python_fastapi_celery_flower_data
  docker compose up -d
  ```

## Useful Commands

```bash
# View Flower logs in real-time
docker compose logs -f flower

# Restart only Flower
docker compose restart flower

# Stop Flower temporarily
docker compose stop flower

# Start Flower again
docker compose start flower

# Access shell inside Flower container
docker compose exec flower sh

# View Flower version
docker compose exec flower flower --version
```

## Additional Resources

- **Official documentation**: <https://flower.readthedocs.io/>
- **GitHub**: <https://github.com/mher/flower>
- **PyPI**: <https://pypi.org/project/flower/>

## Tips

1. **Use Monitor for debugging**: It's the best way to see what's happening in real-time

2. **Filter tasks by state**: In the Tasks panel, use filters to quickly find problematic tasks

3. **Configure alerts**: Flower can send notifications when tasks fail (requires additional configuration)

4. **Export data**: Use Flower's REST API to integrate with external monitoring tools

5. **Performance**: If you have many tasks, consider using persistence to not lose history when restarting

## Integration with the Project

In our project, Flower is configured to:

- ✅ Monitor the Celery worker
- ✅ Connect to RabbitMQ as broker
- ✅ Use the same code base (same Dockerfile)
- ✅ Share environment variables (.env)
- ✅ Port 5555 exposed on host

**Monitoring flow:**

```text
1. You create a task via POST /tasks/ or /tasks/slow
2. The task goes to RabbitMQ
3. The Celery Worker processes the task
4. Flower monitors everything in real-time
5. You visualize in the browser at http://localhost:5555
```

## When to Use Flower vs API Endpoints

### Use Flower when:

- 🎯 You want **visual monitoring** in a browser
- 🔍 Need to **debug failed tasks** with stack traces
- 📊 Want to see **graphs and metrics**
- ⚙️ Need to **control workers** (restart, grow pool, etc.)
- 📈 Want to monitor **system performance**
- 🕐 Need **real-time view** with auto-refresh

### Use API `/tasks/` endpoint when:

- 🤖 You need **programmatic access** from your code
- 📱 Building **custom integrations**
- 🔄 Need **automated monitoring** (CI/CD, alerts, etc.)
- 📝 Want to **integrate with other systems**

**Best practice**: Use **both!**

- Flower for **human monitoring** (development, operations)
- API for **automated integration** (scripts, monitoring tools)

## Important Notes

### RPC Backend Limitations

Our project uses `rpc://` as the Celery result backend, which means:

- ✅ Fast and lightweight
- ✅ Perfect for development
- ❌ **Doesn't persist results** after they're consumed
- ❌ **Limited history** - only recent tasks

**What this means for Flower:**

- You can see **ACTIVE, SCHEDULED, and RESERVED** tasks
- Once a task completes and the result is consumed, it **disappears from Flower**
- No long-term task history

**Solution for production:**

If you need complete history, consider using a persistent backend:

```python
# Option 1: Redis
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Option 2: Database
CELERY_RESULT_BACKEND=db+postgresql://user:pass@db:5432/celery_results
```

### Security Considerations

For production deployments:

1. **Enable authentication**:

   ```yaml
   command: celery -A app.celery_app flower --port=5555 --basic_auth=admin:secret_password
   ```

2. **Use HTTPS** with a reverse proxy (nginx, traefik)

3. **Restrict access** via firewall or VPN

4. **Don't expose** port 5555 publicly

## Complete Example: Create and Monitor Task

### Step-by-step

1. **Start all services**:

   ```bash
   docker compose up -d
   ```

2. **Access Flower**:

   ```bash
   open http://localhost:5555
   ```

3. **Create a slow task** (runs for 20 seconds):

   ```bash
   curl -X POST "http://localhost:8060/tasks/slow?duration=20" | jq
   ```

   Output:

   ```json
   {
     "task_id": "abc123...",
     "status": "PENDING"
   }
   ```

4. **Monitor in Flower**:
   - Go to "Monitor" tab
   - You'll see the task in STARTED state
   - Watch the elapsed time increase
   - After 20 seconds, task completes

5. **Check task details**:
   - Go to "Tasks" tab
   - Click on your task_id
   - See:
     - Arguments: `duration=20`
     - State: SUCCESS
     - Runtime: ~20 seconds
     - Result: `{"message": "Task completed after 20 seconds"}`

6. **View worker info**:
   - Go to "Workers" tab
   - See which worker processed the task
   - Check worker statistics

## FAQ

### Q: Why don't I see completed tasks in Flower?

**A**: With RPC backend, tasks disappear after results are consumed. Use Redis or Database backend for persistent history.

### Q: Can I use Flower in production?

**A**: Yes! But add authentication, use HTTPS, and restrict access. Flower is used by many companies in production.

### Q: How many tasks can Flower handle?

**A**: Thousands! But performance depends on your backend and task rate. For very high volumes (>10k tasks/min), consider sampling.

### Q: Can Flower control task execution?

**A**: Limited. You can control workers (restart, shutdown) but can't cancel individual tasks without additional Celery configuration.

### Q: Does Flower work with other brokers besides RabbitMQ?

**A**: Yes! Flower works with Redis, Amazon SQS, and other Celery-supported brokers.

---

**Happy monitoring with Flower! 🌸**

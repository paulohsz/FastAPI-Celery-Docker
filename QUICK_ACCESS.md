# 🚀 Quick Access Guide

## Quick Access URLs

After starting containers with `docker compose up -d`, access:

### 🌐 APIs and Documentation

| Service | URL | Description |
|---------|-----|-------------|
| **FastAPI** | <http://localhost:8060> | Main REST API |
| **Swagger UI** | <http://localhost:8060/docs> | Interactive API documentation |
| **ReDoc** | <http://localhost:8060/redoc> | Alternative documentation |
| **Health Check** | <http://localhost:8060/health> | Application status |

### 📊 Monitoring

| Service | URL | Credentials | Description |
|---------|-----|-------------|-----------|
| **Flower** | <http://localhost:5555> | - | Real-time Celery monitoring |
| **RabbitMQ Management** | <http://localhost:15672> | guest/guest | Queue management |

### 💾 Database

| Service | Host | Port | Description |
|---------|------|------|-----------|
| **PostgreSQL** | localhost | 5432 | Main database |

**Connection:**

```bash
psql -h localhost -p 5432 -U postgres -d appdb
# Password: postgres
```

---

## 🧪 Quick Test

### 1. Verify Everything is Working

```bash
# Container status
docker compose ps

# API health check
curl http://localhost:8060/health
```

### 2. Create Task and Monitor in Flower

```bash
# Terminal 1: Create 20-second slow task
curl -X POST "http://localhost:8060/tasks/slow?duration=20"

# Copy the returned task_id
# Open browser at http://localhost:5555
# Go to "Tasks" or "Monitor" to see the task executing
```

### 3. Test Message Creation

```bash
# Create message via async task
curl -X POST http://localhost:8060/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from Celery!"}'

# List created messages
curl http://localhost:8060/messages/
```

### 4. View Active Tasks

```bash
# Via API
curl http://localhost:8060/tasks/

# Via Flower (browser)
# http://localhost:5555/tasks
```

---

## 📱 Main Features by Interface

### Flower (<http://localhost:5555>)

- **Dashboard**: Overview with metrics
- **Tasks**: List all tasks (filters by state)
- **Workers**: Worker status and control
- **Monitor**: Real-time visualization
- **Broker**: RabbitMQ information

### Swagger (<http://localhost:8060/docs>)

- **POST /tasks/**: Create message task
- **POST /tasks/slow**: Create slow task (test)
- **GET /tasks/**: List active tasks
- **GET /tasks/{task_id}**: Specific task status
- **GET /messages/**: List all messages
- **POST /messages/**: Create message directly

### RabbitMQ Management (<http://localhost:15672>)

- **Overview**: General statistics
- **Connections**: Active connections
- **Channels**: Communication channels
- **Exchanges**: Message exchanges
- **Queues**: Queues and pending messages

---

## 🔧 Useful Commands

```bash
# View logs in real-time
docker compose logs -f

# View specific logs
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f flower

# Restart specific service
docker compose restart backend
docker compose restart worker
docker compose restart flower

# Stop all containers
docker compose down

# Start all containers
docker compose up -d

# Rebuild and start
docker compose up -d --build

# View resource usage
docker stats
```

---

## 📖 Complete Documentation

- **README.md**: Overview and complete setup
- **FLOWER.md**: Detailed Flower guide
- **TASKS_API.md**: Task API documentation
- **CHANGELOG.md**: Change history

---

## 🎯 Common Use Cases

### Monitor Tasks in Real-Time

1. Open <http://localhost:5555/monitor>
2. In another terminal:

   ```bash
   for i in {1..5}; do
     curl -X POST "http://localhost:8060/tasks/slow?duration=10"
   done
   ```

3. Watch tasks in Flower

### Debug Failed Task

1. Access <http://localhost:5555/tasks>
2. Filter by "FAILURE"
3. Click on task to see details and stack trace

### View RabbitMQ Queues

1. Access <http://localhost:15672>
2. Login: guest/guest
3. Go to "Queues" tab
4. Click on "celery" for details

### Check Active Workers

1. Access <http://localhost:5555/workers>
2. See status, processed tasks, concurrency
3. Use buttons to manage workers (restart, shutdown, etc.)

---

## ⚠️ Quick Troubleshooting

### Container Won't Start

```bash
# View specific error
docker compose logs [service_name]

# Rebuild from scratch
docker compose down -v
docker compose up --build
```

### Flower Not Showing Tasks

1. Check if worker is connected: <http://localhost:5555/workers>
2. Create test task: `curl -X POST "http://localhost:8060/tasks/slow?duration=5"`
3. Check quickly in <http://localhost:5555/monitor>

### Database Problems

```bash
# Reset database (WARNING: deletes data!)
docker compose down -v
docker compose up -d

# Or access and backup first
docker compose exec db pg_dump -U postgres appdb > backup.sql
```

---

## 🎨 Visual Interfaces

### 1. Flower Dashboard

![Dashboard with real-time graphs and metrics]

- Success/failure rate
- Throughput (tasks/second)
- Active workers
- Average execution time

### 2. Swagger UI

![Interactive interface for API testing]

- Automatic documentation
- Endpoint testing
- Request/response schemas
- Usage examples

### 3. RabbitMQ Management

![Queue management console]

- Broker overview
- Queues and messages
- Exchanges and bindings
- Performance metrics

---

## 🚦 Service Status

Quick status check:

```bash
# All containers should be "Up"
docker compose ps

# Should return 200 OK
curl -I http://localhost:8060/health

# Should return 200 OK
curl -I http://localhost:5555

# Should return 200 OK (login required in browser)
curl -I http://localhost:15672
```

---

## 📞 Next Steps

1. ✅ **Explore Flower**: <http://localhost:5555>
2. ✅ **Test API in Swagger**: <http://localhost:8060/docs>
3. ✅ **Create some tasks**: Use POST /tasks/slow
4. ✅ **Monitor in Flower**: See tasks in real-time
5. ✅ **Check RabbitMQ**: <http://localhost:15672>

**Happy exploring! 🎉**

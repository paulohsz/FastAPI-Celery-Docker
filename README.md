# FastAPI + Celery + Docker Application

A complete, production-ready FastAPI application with Celery workers, PostgreSQ   This 2. **Build and start all services** (creates and starts the 5 containers):

   ```bash
   docker compose up --build
   ```

   This command will:
   - 📦 Create Docker images for backend, worker and flower (Python 3.13)
   - 🐘 Start PostgreSQL 16 in the `db` container (port 5432)
   - 🐰 Start RabbitMQ 3 in the `rabbitmq` container (ports 5672/15672)
   - 🚀 Start FastAPI in the `backend` container (port 8060)
   - ⚙️ Start Celery worker in the `worker` container
   - 🌸 Start Flower monitoring in the `flower` container (port 5555)
   - ✅ Automatically create database tables
   - 📊 Run health checks to ensure DB and RabbitMQ are ready

   **Wait** until you see logs like:

   ```text
   backend  | INFO:     Uvicorn running on http://0.0.0.0:8060
   worker   | [YYYY-MM-DD HH:MM:SS,000: INFO/MainProcess] celery@worker ready.
   flower   | [I YYYY-MM-DD HH:MM:SS,000] Flower started
   ```

3. **Access the application** (from your browser/terminal on the host machine):
   - **API**: <http://localhost:8060>
   - **Interactive Documentation (Swagger)**: <http://localhost:8060/docs>
   - **Alternative Documentation (ReDoc)**: <http://localhost:8060/redoc>
   - **RabbitMQ Management UI**: <http://localhost:15672> (username: guest, password: guest)
   - **Flower Monitoring UI**: <http://localhost:5555> (real-time Celery monitoring)📦 Create Docker images for backend and worker (Python 3.13)
   - 🐘 Start PostgreSQL 16 in the `db` container (port 5432)
   - 🐰 Start RabbitMQ 3 in the `rabbitmq` container (ports 5672/15672)
   - 🚀 Start FastAPI in the `backend` container (port 8060)
   - ⚙️ Start Celery worker in the `worker` container
   - ✅ Automatically create database tables
   - 📊 Run health checks to ensure DB and RabbitMQ are readyse, and RabbitMQ message broker, all orchestrated with Docker Compose.

## Features

- **FastAPI** backend with async database operations
- **Celery** distributed task queue for background jobs
- **PostgreSQL** database with SQLAlchemy ORM
- **RabbitMQ** as message broker with Management UI
- **Alembic** for database migrations
- **Docker Compose** for local development environment
- **pytest** for testing with async support
- **ruff** for linting and formatting
- **pre-commit** hooks for code quality

## Technology Stack

### Runtime Dependencies (Python 3.13)

- FastAPI==0.116.2
- uvicorn[standard]==0.24.0
- pydantic[email]==2.11.9
- SQLAlchemy==2.0.43
- pydantic-settings==2.11
- alembic==1.16.5
- celery==5.4.0 (includes kombu and amqp for RabbitMQ support)
- flower==2.0.1 (Celery monitoring tool)
- asyncpg==0.30.0
- psycopg2-binary==2.9.10

### Development Dependencies
- ruff==0.13.0
- pre-commit==4.3.0
- pytest==8.4.2
- httpx==0.28.1
- pytest-cov==7.0.0
- taskipy==1.3.0
- pytest-asyncio==0.24.0

## Architecture

This project uses **5 Docker containers** orchestrated with Docker Compose:

1. **`db`** - PostgreSQL 16 (Alpine Linux)
   - Stores application data
   - Port: 5432
   - Persistent volume for data

2. **`rabbitmq`** - RabbitMQ 3 with Management (Alpine Linux)
   - Message broker for Celery
   - AMQP protocol on port 5672
   - Management UI on port 15672
   - Access Management UI at <http://localhost:15672> (guest/guest)
   - Persistent volume for data

3. **`backend`** - FastAPI Application (Python 3.13)
   - Container with Python + FastAPI + uvicorn
   - Asynchronous web server
   - Port: 8060
   - Hot-reload enabled for development

4. **`worker`** - Celery Worker (Python 3.13)
   - Container with Python + Celery
   - Processes asynchronous background tasks
   - Uses the same code as backend (same Dockerfile)

5. **`flower`** - Flower Monitoring (Python 3.13)
   - Container with Celery Flower
   - Real-time monitoring of Celery tasks and workers
   - Port: 5555
   - Web UI at <http://localhost:5555>

**Important:** FastAPI, Celery and Flower run in separate Python containers, not on the host machine!

## Project Structure

```
.
├── docker-compose.yml          # Docker Compose orchestration (4 services)
├── rabbitmq.conf               # RabbitMQ configuration (disables deprecated features)
├── README.md                   # This file
└── backend/
    ├── Dockerfile              # Docker image for backend and worker containers
    ├── requirements.txt        # Python runtime dependencies
    ├── requirements-dev.txt    # Python dev dependencies
    ├── .env                    # Environment variables
    ├── pyproject.toml          # Project config and taskipy tasks
    ├── .pre-commit-config.yaml # Pre-commit hooks configuration
    ├── alembic.ini             # Alembic configuration
    ├── alembic/
    │   ├── env.py              # Alembic environment setup
    │   ├── script.py.mako      # Migration template
    │   └── versions/
    │       └── 20241016_1200_001_initial_migration.py
    ├── app/
    │   ├── __init__.py
    │   ├── main.py             # FastAPI application (runs in backend container)
    │   ├── config.py           # Settings management
    │   ├── db.py               # Database setup (async & sync)
    │   ├── models.py           # SQLAlchemy models
    │   ├── schemas.py          # Pydantic schemas
    │   ├── crud.py             # CRUD operations
    │   ├── celery_app.py       # Celery configuration (optimized for RabbitMQ 3.x)
    │   └── tasks.py            # Celery tasks (run in worker container)
    └── tests/
        ├── __init__.py
        └── test_api.py         # API tests
```

## Getting Started

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose (included in Docker Desktop)

**Note:** You **DO NOT need** to install Python, FastAPI, Celery or any dependencies on your machine. Everything runs inside Docker containers!

## Development with VS Code Dev Containers

For a complete development experience with persistent extensions and configurations:

### 🚀 Attach to Container (Recommended)

1. **Start the containers:**
   ```bash
   docker compose up -d
   ```

2. **In VS Code:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type: `Dev Containers: Attach to Running Container`
   - Select: `learning_python_fastapi_celery-backend-1`

3. **Automatic setup includes:**
   - ✅ Python extension with linting and formatting
   - ✅ Black formatter configured
   - ✅ Pylint & Flake8 linting enabled
   - ✅ GitLens for advanced Git features
   - ✅ REST Client for API testing
   - ✅ Docker and PostgreSQL extensions
   - ✅ Jupyter notebook support
   - ✅ Port forwarding (8060) configured
   - ✅ Python interpreter automatically detected

See [`.devcontainer/README.md`](.devcontainer/README.md) for detailed instructions and customization options.

### Quick Start

1. **Clone or copy all files** to your project directory with the structure shown above.

2. **Build and start all services** (creates and starts the 4 containers):
   ```bash
   docker compose up --build
   ```

   This command will:
   - 📦 Create Docker images for backend and worker (Python 3.12)
   - 🐘 Start PostgreSQL 16 in the `db` container (port 5432)
   - � Start RabbitMQ 3 in the `rabbitmq` container (ports 5672/15672)
   - 🚀 Start FastAPI in the `backend` container (port 8060)
   - ⚙️ Start Celery worker in the `worker` container
   - ✅ Automatically create database tables
   - 📊 Run health checks to ensure DB and RabbitMQ are ready

   **Wait** until you see logs like:
   ```
   backend  | INFO:     Uvicorn running on http://0.0.0.0:8060
   worker   | [YYYY-MM-DD HH:MM:SS,000: INFO/MainProcess] celery@worker ready.
   ```

3. **Access the application** (from your browser/terminal on the host machine):
   - API: http://localhost:8060
   - Interactive Documentation (Swagger): http://localhost:8060/docs
   - Alternative Documentation (ReDoc): http://localhost:8060/redoc
   - RabbitMQ Management UI: http://localhost:15672 (username: guest, password: guest)

### Checking Containers

```bash
# View running containers
docker compose ps

# View logs from all services
docker compose logs -f

# View logs from a specific service
docker compose logs -f backend
docker compose logs -f worker
```

### Running Commands in Containers

Since everything runs in containers, you need to use `docker compose exec` or `docker compose run`:

```bash
# Execute command in a running container
docker compose exec backend <command>

# Execute command in a new container (useful if the service is not running)
docker compose run --rm backend <command>
```

### Running Database Migrations

The application automatically creates tables on startup (development only). For production, use Alembic:

```bash
# Run migrations (inside backend container)
docker compose run --rm backend alembic upgrade head

# Create a new migration
docker compose run --rm backend alembic revision --autogenerate -m "add_new_column"

# View migration history
docker compose run --rm backend alembic history

# View current status
docker compose run --rm backend alembic current

# Or use taskipy (if the container is already running)
docker compose exec backend task migrate
```

### Using Taskipy (Command Shortcuts)

Inside the backend container, you can use taskipy shortcuts:

```bash
# Start FastAPI server (manual - docker-compose usually starts it automatically)
docker compose exec backend task start

# Start Celery worker (manual)
docker compose exec backend task worker

# Run migrations
docker compose exec backend task migrate

# Run tests
docker compose exec backend task test

# Run tests with coverage
docker compose exec backend task test-cov

# Lint (check code)
docker compose exec backend task lint

# Lint with auto-fix
docker compose exec backend task lint-fix

# Format code
docker compose exec backend task format
```

### Interactive Python Shell in Container

```bash
# Access Python shell in backend container
docker compose exec backend python

# Or bash shell to explore the container
docker compose exec backend bash

# Or Celery shell to debug tasks
docker compose exec worker bash
```

### Installing New Dependencies

If you add new Python libraries:

```bash
# 1. Add to requirements.txt or requirements-dev.txt
# 2. Rebuild the container
docker compose up --build backend

# Or rebuild all containers
docker compose up --build
```

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint

### Message Endpoints

- `POST /messages/` - Create a message directly (synchronous)
  ```bash
  curl -X POST "http://localhost:8060/messages/" \
    -H "Content-Type: application/json" \
    -d '{"content": "Hello, World!"}'
  ```

- `GET /messages/` - List all messages
  ```bash
  curl "http://localhost:8060/messages/"
  ```

### Task Endpoints (Celery)

- `POST /tasks/` - Enqueue a background task to create a message
  ```bash
  curl -X POST "http://localhost:8060/tasks/" \
    -H "Content-Type: application/json" \
    -d '{"content": "Async message via Celery"}'
  ```

- `GET /tasks/{task_id}` - Get task status and result
  ```bash
  # Replace TASK_ID with the actual task ID from the previous response
  curl "http://localhost:8060/tasks/TASK_ID"
  ```

### Example Workflow

1. **Enqueue a task**:
   ```bash
   curl -X POST "http://localhost:8060/tasks/" \
     -H "Content-Type: application/json" \
     -d '{"content": "My async task"}' \
     | jq
   ```
   Response:
   ```json
   {
     "task_id": "abc123-def456-...",
     "status": "PENDING",
     "message": "Task enqueued successfully"
   }
   ```

2. **Check task status**:
   ```bash
   curl "http://localhost:8060/tasks/abc123-def456-..." | jq
   ```
   Response:
   ```json
   {
     "task_id": "abc123-def456-...",
     "status": "SUCCESS",
     "result": {
       "id": 1,
       "content": "My async task",
       "created_at": "2025-10-16T12:00:00"
     }
   }
   ```

3. **List all messages**:
   ```bash
   curl "http://localhost:8060/messages/" | jq
   ```

## Testing

### Running Tests

**Important:** Tests run **inside the backend container**, not on your local machine!

```bash
# Run all tests
docker compose exec backend pytest

# Run with verbose output
docker compose exec backend pytest -v

# Run specific tests
docker compose exec backend pytest tests/test_api.py::test_create_message_direct

# Run with code coverage
docker compose exec backend pytest --cov=app --cov-report=html --cov-report=term

# Or use taskipy
docker compose exec backend task test
docker compose exec backend task test-cov
```

### Viewing Test Coverage

```bash
# After running tests with coverage
docker compose exec backend pytest --cov=app --cov-report=html

# Copy HTML report to host machine
docker compose cp backend:/app/htmlcov ./htmlcov

# Open in browser
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Test Notes

The included tests demonstrate:
- ✅ API endpoint testing
- ✅ Message creation and retrieval
- ✅ Celery task enqueuing

**Important:** Tests that verify complete task execution (enqueue → worker processes → result) require a running Celery worker and are integration tests. The provided tests verify the API works correctly but don't wait for task completion. For full integration testing, you would need to:

1. Ensure worker is running
2. Poll the task status endpoint until completion
3. Verify the result

### Running Integration Tests (with Worker)

If you want to test the complete flow including task processing:

```bash
# 1. Make sure all services are running
docker compose up -d

# 2. Execute the tests
docker compose exec backend pytest -v

# 3. For tests that wait for tasks, you can add delays
docker compose exec backend pytest -v --log-cli-level=INFO
```

## Development

### Setting Up Pre-commit Hooks

```bash
# Install pre-commit hooks (inside container)
docker compose exec backend pre-commit install

# Run hooks manually
docker compose exec backend pre-commit run --all-files
```

### Code Quality

```bash
# Lint - check code
docker compose exec backend ruff check .

# Lint - check and auto-fix
docker compose exec backend ruff check . --fix

# Format - format code
docker compose exec backend ruff format .

# Or use taskipy
docker compose exec backend task lint
docker compose exec backend task lint-fix
docker compose exec backend task format
```

### Debugging

For comprehensive debugging setup with breakpoints, variable inspection, and step-through debugging:

**🚀 Quick Debug Setup:**

1. **Start debug environment:**
   ```bash
   docker compose -f docker-compose.debug.yml up --build
   ```

2. **In VS Code:**
   - Set breakpoints in your code
   - Go to Run & Debug (`Ctrl+Shift+D`)
   - Select "FastAPI Debug (Remote Attach)"
   - Press F5

3. **Test with breakpoints:**
   ```bash
   curl -X POST http://localhost:8060/tasks/slow?duration=5
   ```

**Available debug configurations:**
- 🐛 **FastAPI Debug** - Debug web endpoints
- 🔄 **Celery Debug** - Debug background tasks  
- 🧪 **Test Debug** - Debug unit tests
- 📁 **File Debug** - Debug any Python file

See [`DEBUG.md`](DEBUG.md) for complete debugging guide with examples.

### Viewing Container Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend   # FastAPI
docker compose logs -f worker    # Celery
docker compose logs -f db        # PostgreSQL
docker compose logs -f flower    # Flower

# Last N lines
docker compose logs --tail=100 backend

# Logs since a specific time
docker compose logs --since YYYY-MM-DDTHH:MM:SS backend
```

### Accessing the Database (PostgreSQL)

```bash
# Connect to PostgreSQL via psql
docker compose exec db psql -U postgres -d appdb

# Inside psql, you can execute SQL queries:
# \dt              # list tables
# \d messages      # view messages table structure
# SELECT * FROM messages;  # view all records

# Execute query directly
docker compose exec db psql -U postgres -d appdb -c "SELECT * FROM messages;"

# Database backup
docker compose exec db pg_dump -U postgres appdb > backup.sql

# Restore backup
docker compose exec -T db psql -U postgres appdb < backup.sql
```

### Accessing RabbitMQ Management UI

RabbitMQ includes a built-in web-based management interface:

```bash
# Access via browser
# URL: http://localhost:15672
# Username: guest
# Password: guest
```

**Features:**
- 📊 Monitor queues, exchanges, and connections
- 🔍 View Celery task queues in real-time
- 📈 View message rates and statistics
- 🐛 Debug message routing and delivery
- ⚙️ Manage virtual hosts and permissions
- 📋 View and purge messages from queues

**Useful for:**
- 🔍 Inspecting Celery task queues (look for "celery" queue)
- 📊 Monitoring message throughput and delivery
- � Debugging task processing issues
- �️ Purging queues when needed
- � Viewing performance metrics

### Monitoring Celery Tasks

```bash
# View worker logs in real-time
docker compose logs -f worker

# Inspect active tasks
docker compose exec worker celery -A app.celery_app inspect active

# View registered tasks
docker compose exec worker celery -A app.celery_app inspect registered

# View statistics
docker compose exec worker celery -A app.celery_app inspect stats

# Using RabbitMQ Management UI:
# 1. Open http://localhost:15672 (guest/guest)
# 2. Go to "Queues" tab
# 3. Look for "celery" queue to see pending tasks
# 4. Click on the queue to view messages and details
```

### Restarting Specific Services

```bash
# Restart only backend (FastAPI)
docker compose restart backend

# Restart only worker (Celery)
docker compose restart worker

# Restart and rebuild (after Dockerfile changes)
docker compose up -d --build backend

# Stop a specific service
docker compose stop backend

# Start a stopped service
docker compose start backend
```

### Stopping and Cleaning Up

```bash
# Stop all containers
docker compose down

# Stop and remove volumes (CAUTION: deletes database data!)
docker compose down -v

# Stop, remove volumes and images
docker compose down -v --rmi all

# Clean orphaned containers, networks and volumes
docker system prune -a --volumes
```

## Production Considerations

### Remove Auto-Table Creation

In `backend/app/main.py`, the `lifespan` function automatically creates database tables on startup. **This is for development only**.

For production:
1. Remove or comment out the table creation code in the `lifespan` function:
   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       """Startup and shutdown events."""
       # REMOVE THIS FOR PRODUCTION:
       # async with async_engine.begin() as conn:
       #     await conn.run_sync(Base.metadata.create_all)
       yield
       await async_engine.dispose()
   ```

2. Use Alembic migrations exclusively:
   ```bash
   docker compose run --rm backend alembic upgrade head
   ```

### Multi-stage Docker Build

For production, modify the Dockerfile to use multi-stage builds:
- Build stage: Install all dependencies
- Production stage: Copy only runtime dependencies and exclude dev packages

### RabbitMQ Configuration

This project is configured to work with RabbitMQ 3.x and avoid deprecated features warnings:

**Celery optimizations:**
- ✅ Uses durable queues (not transient) - fixes `transient_nonexcl_queues` warning
- ✅ Uses per-queue QoS instead of global - fixes `global_qos` warning
- ✅ Configures explicit queue settings with proper durability
- ✅ Uses `broker_connection_retry_on_startup` for better reliability

**RabbitMQ server configuration:**
- Deprecated features are disabled by default
- This ensures compatibility with future RabbitMQ versions
- No warnings in logs about deprecated features

If you need to re-enable deprecated features for legacy compatibility, modify `docker-compose.yml`:
```yaml
environment:
  RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS: >-
    -rabbitmq_deprecated_features permitted_by_default true
```

### Environment Variables

The `.env` file contains development defaults. For production:
- Use strong passwords
- Use environment-specific URLs
- Store secrets securely (e.g., Docker secrets, Kubernetes secrets, AWS Parameter Store)
- Set `DEBUG=False`

### Security

- Change default PostgreSQL credentials
- Use Redis password authentication
- Enable TLS/SSL for database connections
- Implement rate limiting
- Add authentication/authorization to API endpoints
- Use HTTPS in production
- Regular security updates for base images

### Scaling

- Increase number of Celery workers:
  ```bash
  docker compose up --scale worker=3
  ```
- Use a process manager like supervisor or systemd for production deployments
- Consider using Kubernetes for orchestration
- Implement connection pooling for database
- Use Redis Sentinel for high availability

## Troubleshooting

### Containers Not Starting

**Check if ports are already in use:**
```bash
lsof -i :5432  # PostgreSQL
lsof -i :5672  # RabbitMQ AMQP
lsof -i :15672 # RabbitMQ Management UI
lsof -i :8060  # FastAPI

# If any port is in use, stop the process or change the port in docker-compose.yml
```

**Check error logs:**
```bash
docker compose logs backend
docker compose logs worker
docker compose logs db
docker compose logs rabbitmq
```

### Database Connection Errors

**Check if PostgreSQL is ready:**
```bash
# Check container health
docker compose ps

# Test connection
docker compose exec db pg_isready -U postgres

# View database logs
docker compose logs db
```

**If you get "connection refused" or "database not ready" errors:**
- The backend and worker containers have `depends_on` with health checks
- Wait a few seconds until the database is ready
- Docker Compose waits automatically

### Celery Tasks Not Executing

**Check worker logs:**
```bash
docker compose logs -f worker

# Look for:
# - "celery@worker ready" (worker started)
# - "Task app.tasks.create_message_task" (task received)
# - Connection errors with RabbitMQ or database
```

**Check RabbitMQ connection:**
```bash
# Check RabbitMQ health
docker compose exec rabbitmq rabbitmq-diagnostics ping

# Check if RabbitMQ is accepting connections
docker compose logs rabbitmq | grep "Server startup complete"
```

**Check RabbitMQ Management UI:**
- Open http://localhost:15672
- Login with guest/guest
- Go to "Queues" tab
- Verify "celery" queue exists and has consumers

**Check if worker registered the tasks:**
```bash
docker compose exec worker celery -A app.celery_app inspect registered
```

### "ModuleNotFoundError" or "ImportError"

**This means dependencies were not installed:**
```bash
# Rebuild containers
docker compose down
docker compose up --build

# Check if requirements.txt is correct
docker compose exec backend pip list
```

### Backend or Worker Container Keeps Restarting

**View logs to identify the error:**
```bash
docker compose logs backend
docker compose logs worker

# Common errors:
# - Invalid Python syntax
# - Module not found
# - Connection error with DB/Redis
```

### Code Changes Not Reflecting

**Hot-reload is enabled, but if it doesn't work:**
```bash
# 1. Check if volume is mounted
docker compose exec backend ls -la /app

# 2. Restart the container
docker compose restart backend

# 3. If you changed requirements.txt or Dockerfile, rebuild
docker compose up --build backend
```

### Clean Everything and Start Over

```bash
# Stop and remove EVERYTHING (containers, networks, volumes, images)
docker compose down -v --rmi all

# Clean Docker cache
docker system prune -a --volumes

# CAUTION: This deletes ALL data including PostgreSQL and RabbitMQ!
# Backup database first if necessary.

# Rebuild from scratch
docker compose up --build
```

### Build Without Cache

**If changes are not being applied or you need a completely clean build:**

```bash
# Build without cache, then start
docker compose build --no-cache
docker compose up

# Or in one command (force recreate containers)
docker compose up --build --force-recreate

# Most complete clean rebuild
docker compose down -v --rmi all
docker compose build --no-cache
docker compose up
```

**When to use `--no-cache`:**
- Changes in Dockerfile not being applied
- Dependency caching issues
- After updating base images (e.g., python:3.13-slim)
- To ensure a completely clean build

### Performance Issues (macOS/Windows)

**Docker Desktop can be slow with volumes:**
```bash
# Option 1: Use named volumes instead of bind mounts (in production)
# Option 2: Adjust Docker Desktop settings
# Option 3: Use Docker with WSL2 (Windows) or Colima (macOS)
```

### Check Container Health

```bash
# View status of all containers
docker compose ps

# View resources being used
docker stats

# Inspect specific container
docker compose exec backend ps aux
docker compose exec backend df -h  # disk space
```

### Corrupted Database

```bash
# Stop everything
docker compose down

# Remove PostgreSQL volume
docker volume rm learning_python_fastapi_celery_postgres_data

# Remove RabbitMQ volume (if needed)
docker volume rm learning_python_fastapi_celery_rabbitmq_data

# Recreate everything
docker compose up --build

# Tables will be recreated automatically
```

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests!

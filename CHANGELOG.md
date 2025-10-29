# Changelog

## Latest Release - Flower Integration

### Added

- **Flower monitoring tool** integrated as a 5th Docker container
  - Real-time monitoring of Celery workers and tasks
  - Web UI accessible at <http://localhost:5555>
  - Visual dashboard with task statistics and graphs
  - Worker management (shutdown, restart, pool control)
  - Task filtering and search capabilities
  - REST API for programmatic access

### Changed

- Updated `backend/requirements.txt`: Added `flower==2.0.1`
- Updated `docker-compose.yml`: Added `flower` service on port 5555
- Updated `README.md`: Architecture now shows 5 containers
- Updated Quick Start guide with Flower access information

### Documentation

- Created `FLOWER.md`: Comprehensive guide for Flower usage
  - Dashboard overview
  - Tasks monitoring
  - Workers management
  - Broker information
  - Real-time monitoring
  - API endpoints
  - Troubleshooting guide

### Benefits

- ✅ Real-time task visualization
- ✅ Historical task data (limited by backend)
- ✅ Worker health monitoring
- ✅ Performance metrics and graphs
- ✅ Easy debugging of failed tasks
- ✅ No code changes required in application

---

## Previous Update - Python 3.13 Update

### Changed

- **Upgraded Python version from 3.12 to 3.13** in Docker containers
  - Updated `backend/Dockerfile`: `FROM python:3.13-slim`
  - Both backend and worker containers now use Python 3.13.9
  - All dependencies are compatible with Python 3.13

### Updated Documentation

- README.md updated to reflect Python 3.13
  - Technology Stack section
  - Architecture section (container descriptions)
  - Quick Start instructions
  - Rebuild instructions

### Verified

- ✅ All 4 containers build and start successfully
- ✅ FastAPI backend running on Python 3.13.9
- ✅ Celery worker running on Python 3.13.9
- ✅ PostgreSQL 16 connection working
- ✅ RabbitMQ 3 message broker working
- ✅ API health endpoint responding correctly
- ✅ All dependencies installed successfully

### Notes

- RabbitMQ deprecation warnings remain (as decided, they don't impact functionality)
- No breaking changes in application code
- Configuration remains unchanged

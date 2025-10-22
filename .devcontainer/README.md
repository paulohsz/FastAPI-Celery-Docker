# Dev Container Configuration

This directory contains the configuration for VS Code Dev Containers, which allows you to have a consistent development environment with pre-installed extensions and settings.

## What's Included

### Pre-installed Extensions

**Python Development:**
- Python extension pack
- Black formatter
- Pylint & Flake8 linters  
- isort for import organization
- Jupyter notebooks support

**FastAPI/Web Development:**
- JSON support
- YAML support
- Docker extension
- REST Client for API testing
- OpenAPI/Swagger support

**Code Quality:**
- GitLens for Git integration
- Code spell checker
- Prettier formatter
- ESLint

**Database:**
- PostgreSQL extension for database management

**Productivity:**
- VS Code Icons
- Remote Containers extension

### Automatic Settings

- Python interpreter configured
- Black formatting on save  
- Import organization on save
- Linting enabled (Pylint + Flake8)
- Pytest configured for testing
- FastAPI port (8060) forwarded automatically

## How to Use

### Method 1: Attach to Running Container

1. Start your containers:
   ```bash
   docker compose up -d
   ```

2. In VS Code:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Dev Containers: Attach to Running Container"
   - Select the backend container (usually `learning_python_fastapi_celery-backend-1`)

3. VS Code will:
   - Connect to the container
   - Install all configured extensions automatically
   - Apply the development settings
   - Set up the Python environment

### Method 2: Reopen in Container

1. Open the project in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)  
3. Type "Dev Containers: Reopen in Container"
4. Select "FastAPI + Celery Backend"

This will automatically start the backend service and attach VS Code to it.

## Benefits

### ✅ Persistent Extensions
- Extensions are automatically installed every time you attach
- No need to manually install Python, linting, or formatting extensions
- Consistent development environment across different machines

### ✅ Pre-configured Settings
- Python interpreter automatically detected
- Formatting and linting configured and working
- Testing environment ready
- Port forwarding configured

### ✅ Isolated Environment
- Development happens inside the container
- Same Python version and dependencies as production
- No conflicts with local Python installations

## Customization

You can modify `.devcontainer/devcontainer.json` to:

### Add More Extensions

```json
"extensions": [
  "ms-python.python",
  "your-new-extension-id"
]
```

### Change Settings

```json
"settings": {
  "python.formatting.provider": "autopep8",  // Change from black
  "editor.tabSize": 2  // Change tab size
}
```

### Add Development Dependencies

```json
"postCreateCommand": "pip install pytest-cov mypy"
```

## Troubleshooting

### Extensions Not Installing

If extensions don't install automatically:

1. Check that you're connected to the container
2. Manually install missing extensions
3. Check VS Code logs: `View > Output > Dev Containers`

### Python Interpreter Not Found

If Python isn't detected:

1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"  
3. Choose `/usr/local/bin/python`

### Port Forwarding Issues

If you can't access the FastAPI app:

1. Check the Ports tab in VS Code terminal panel
2. Manually forward port 8060
3. Or access via container IP

### Container Connection Failed

If attachment fails:

1. Make sure containers are running: `docker compose ps`
2. Try restarting containers: `docker compose restart backend`
3. Check Docker logs: `docker compose logs backend`

## Files Structure

```
.devcontainer/
├── devcontainer.json     # Main configuration
└── README.md            # This file
```

## Tips

### Quick Commands Inside Container

Once connected, you can use the integrated terminal:

```bash
# Run the FastAPI app (already running via docker-compose)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8060

# Run tests
pytest

# Format code
black .

# Check linting
flake8 app/

# Install new packages
pip install some-package
```

### Debugging

- Set breakpoints in your Python code
- Use the Debug panel (`Ctrl+Shift+D`)
- Python debugging is pre-configured

### Testing

- Tests are discoverable in the Test Explorer
- Run individual tests by clicking the play button
- Or run all tests with `Ctrl+;` then `A`

## What Happens When You Attach

1. **VS Code connects** to the running backend container
2. **Extensions install** automatically (first time takes ~1-2 minutes)
3. **Settings apply** (Python interpreter, formatting, etc.)
4. **Port forwarding** activates (port 8060 available)
5. **Ready to code!**

Your workspace will be at `/app` inside the container, which maps to the `backend/` directory on your host.

---

**Happy coding with Dev Containers! 🐳✨**
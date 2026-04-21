# How to Run the FastAPI Application

## Understanding the Setup

You're using **`uv`** for Python dependency management. This means:
- Dependencies are defined in `pyproject.toml`
- Dependencies are installed in a virtual environment managed by `uv`
- You need to run commands through `uv` to use those dependencies

## ❌ Wrong Way (Will Fail)

```bash
# This uses system Python (no dependencies installed)
python main.py
# Error: ModuleNotFoundError: No module named 'fastapi'

# This also won't work
cd backend
python app/main.py
# Error: ModuleNotFoundError: No module named 'fastapi'
```

## ✅ Correct Ways to Run

### Method 1: Using `uv run` (Recommended)

```bash
# From project root
cd backend
uv run uvicorn app.main:app --reload

# Or with custom host/port
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Method 2: Activate Virtual Environment First

```bash
# From project root
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows

# Then run normally
cd backend
uvicorn app.main:app --reload
```

### Method 3: Using the main.py directly (with uv)

```bash
# From project root
cd backend
uv run python -m app.main
```

## Why This Happens

### The Problem
When you run `python main.py`:
1. It uses your **system Python** (e.g., `/usr/bin/python3`)
2. System Python doesn't have FastAPI installed
3. You get `ModuleNotFoundError`

### The Solution
When you run `uv run uvicorn app.main:app`:
1. `uv` activates the virtual environment
2. Virtual environment has all dependencies from `pyproject.toml`
3. FastAPI is available ✅

## Quick Reference

### Start Development Server
```bash
cd backend
uv run uvicorn app.main:app --reload
```

### Start Production Server
```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Check if Server is Running
```bash
curl http://localhost:8000/api/health
```

### View API Documentation
Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Stop Server
Press `CTRL+C` in the terminal

## Understanding `uv`

`uv` is a fast Python package manager that:
- Manages virtual environments automatically
- Installs dependencies from `pyproject.toml`
- Ensures consistent environments across machines

### Common `uv` Commands

```bash
# Install/sync dependencies
uv sync

# Add a new dependency
uv add package-name

# Remove a dependency
uv remove package-name

# Run a command in the virtual environment
uv run <command>

# Show installed packages
uv pip list
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Cause:** Running with system Python instead of uv environment
**Solution:** Use `uv run` prefix or activate virtual environment

### Issue: "Port 8000 already in use"
**Cause:** Another process is using port 8000
**Solution:** 
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill

# Or use a different port
uv run uvicorn app.main:app --port 8001
```

### Issue: "Command not found: uv"
**Cause:** uv is not installed
**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: Dependencies not found after adding to pyproject.toml
**Cause:** Need to sync dependencies
**Solution:**
```bash
uv sync
```

## Best Practices

1. **Always use `uv run`** for running commands
2. **Keep `pyproject.toml` updated** with all dependencies
3. **Run `uv sync`** after pulling changes from git
4. **Use `--reload`** flag during development for auto-restart
5. **Check logs** if server doesn't start

## Example Workflow

```bash
# 1. Navigate to project
cd /path/to/product-search-agent

# 2. Sync dependencies (if needed)
uv sync

# 3. Navigate to backend
cd backend

# 4. Start development server
uv run uvicorn app.main:app --reload

# 5. In another terminal, test the API
curl http://localhost:8000/api/health

# 6. Open browser to view docs
open http://localhost:8000/docs

# 7. When done, stop server with CTRL+C
```

## Summary

✅ **DO:** `uv run uvicorn app.main:app --reload`
❌ **DON'T:** `python main.py`

The key is to always run commands through `uv` so it uses the correct virtual environment with all dependencies installed!



-------------------------------------------
# Find the process
lsof -ti:8000 | xargs kill

# Then start again
cd backend
uv run uvicorn app.main:app --reload

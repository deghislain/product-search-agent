# Database Initialization Script

This document provides a guide for using the `init_db.py` script to manage your database.

## Overview

The `init_db.py` script provides a comprehensive set of tools for initializing, managing, and maintaining the database. It can be used both as a command-line tool and as a Python module.

## Command-Line Usage

### Basic Syntax

```bash
python -m app.models.init_db [action] [options]
```

### Available Actions

#### 1. Initialize Database (`init`)

Creates all database tables if they don't exist.

```bash
python -m app.models.init_db init
```

**Output:**
- Lists all tables created
- Safe to run multiple times (won't modify existing tables)

#### 2. Verify Database (`verify`)

Checks database connection and verifies all required tables exist.

```bash
python -m app.models.init_db verify
```

**Output:**
- Database connection status
- List of existing tables
- Table details (columns, indexes, foreign keys)

#### 3. Show Statistics (`stats`)

Displays record counts for all tables.

```bash
python -m app.models.init_db stats
```

**Output:**
- Count of records in each table
- Total record count

#### 4. Drop Database (`drop`)

⚠️ **WARNING:** Deletes all tables and data!

```bash
python -m app.models.init_db drop
```

**Features:**
- Requires confirmation by default
- Use `--no-confirm` to skip confirmation (dangerous!)

#### 5. Reset Database (`reset`)

⚠️ **WARNING:** Drops and recreates all tables!

```bash
python -m app.models.init_db reset
```

**Features:**
- Combines `drop` and `init` actions
- Requires confirmation by default
- Use `--no-confirm` to skip confirmation (dangerous!)

### Command-Line Options

#### `--no-confirm`

Skip confirmation prompts for destructive operations.

```bash
python -m app.models.init_db drop --no-confirm
python -m app.models.init_db reset --no-confirm
```

⚠️ **Use with caution!** This will delete data without asking.

#### `--quiet`

Suppress output messages (useful for scripts).

```bash
python -m app.models.init_db init --quiet
```

#### `--help`

Show help message with all available options.

```bash
python -m app.models.init_db --help
```

## Programmatic Usage

You can also import and use the functions in your Python code.

### Import Functions

```python
from app.models.init_db import (
    init_db,
    verify_db,
    get_db_stats,
    drop_db,
    reset_db
)
```

### Initialize Database

```python
from app.models.init_db import init_db

# With verbose output
success = init_db(verbose=True)

# Without verbose output
success = init_db(verbose=False)

if success:
    print("Database initialized!")
```

### Verify Database

```python
from app.models.init_db import verify_db

# Check if database is properly configured
if verify_db():
    print("Database is ready!")
else:
    print("Database needs initialization")
```

### Get Statistics

```python
from app.models.init_db import get_db_stats

# Get record counts
stats = get_db_stats(verbose=False)

print(f"Search Requests: {stats['search_requests']}")
print(f"Products: {stats['products']}")
print(f"Total Records: {sum(stats.values())}")
```

### Drop Database

```python
from app.models.init_db import drop_db

# Drop with confirmation
drop_db(verbose=True, confirm=True)

# Drop without confirmation (dangerous!)
drop_db(verbose=False, confirm=False)
```

### Reset Database

```python
from app.models.init_db import reset_db

# Reset with confirmation
reset_db(verbose=True, confirm=True)

# Reset without confirmation (dangerous!)
reset_db(verbose=False, confirm=False)
```

## Common Use Cases

### First-Time Setup

When setting up the application for the first time:

```bash
python -m app.models.init_db init
python -m app.models.init_db verify
```

### Development Reset

When you need to reset the database during development:

```bash
python -m app.models.init_db reset
```

### Production Deployment

For production deployments, use the programmatic approach:

```python
from app.models.init_db import init_db, verify_db

# Initialize database
if not verify_db(verbose=False):
    print("Initializing database...")
    init_db(verbose=True)
else:
    print("Database already initialized")
```

### Health Check

Check database health in monitoring scripts:

```python
from app.models.init_db import verify_db, get_db_stats

# Verify database
if not verify_db(verbose=False):
    alert("Database verification failed!")
    
# Check for data
stats = get_db_stats(verbose=False)
if sum(stats.values()) == 0:
    alert("Database is empty!")
```

## Database Schema

The script manages the following tables:

1. **search_requests** - User search criteria
2. **search_executions** - Individual search runs
3. **products** - Scraped product listings
4. **notifications** - User notifications

### Relationships

```
search_requests (1) ──→ (many) search_executions
search_executions (1) ──→ (many) products
search_requests (1) ──→ (many) notifications
products (1) ──→ (many) notifications
```

## Error Handling

All functions return boolean values or dictionaries:

- `init_db()` → `bool` (True if successful)
- `verify_db()` → `bool` (True if database is valid)
- `get_db_stats()` → `dict` (empty dict on error)
- `drop_db()` → `bool` (True if successful)
- `reset_db()` → `bool` (True if successful)

Example error handling:

```python
from app.models.init_db import init_db

try:
    if not init_db(verbose=False):
        print("Failed to initialize database")
        # Handle error
except Exception as e:
    print(f"Error: {e}")
    # Handle exception
```

## Best Practices

1. **Always verify** after initialization:
   ```bash
   python -m app.models.init_db init
   python -m app.models.init_db verify
   ```

2. **Use confirmation** for destructive operations:
   ```bash
   # Good - requires confirmation
   python -m app.models.init_db drop
   
   # Dangerous - no confirmation
   python -m app.models.init_db drop --no-confirm
   ```

3. **Check statistics** regularly:
   ```bash
   python -m app.models.init_db stats
   ```

4. **Use programmatic API** in production:
   ```python
   # Better for production
   from app.models.init_db import init_db
   init_db(verbose=False)
   ```

## Troubleshooting

### Database file not found

```bash
# Initialize the database
python -m app.models.init_db init
```

### Tables missing

```bash
# Verify and recreate if needed
python -m app.models.init_db verify
python -m app.models.init_db init
```

### Corrupted database

```bash
# Reset the database (will delete all data!)
python -m app.models.init_db reset
```

### Permission errors

Ensure the application has write permissions to the database directory.

## See Also

- [Database Models Documentation](../models/)
- [Configuration Guide](../../docs/CONFIG_README.md)
- [Implementation Plan](../../docs/IMPLEMENTATION_PLAN.md)

---

**Made with Bob** 🤖
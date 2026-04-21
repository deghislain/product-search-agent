# Python Logging Explanation

## Why You Weren't Seeing Output

When you added `logger = logging.getLogger(__name__)` to your test file, you created a logger but **didn't configure it**. In Python, loggers need three things to work:

1. **A logger instance** - `logging.getLogger(__name__)` ✅ You had this
2. **A handler** - Where to send the logs (console, file, etc.) ❌ Missing
3. **A log level** - What severity to show (DEBUG, INFO, WARNING, ERROR) ❌ Missing

Without configuration, the logger exists but doesn't output anything!

## The Fix

Added this configuration at the top of your test file:

```python
# Configure logging to show output
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple format for test output
)
logger = logging.getLogger(__name__)
```

### What This Does

- **`logging.basicConfig()`** - Configures the root logger
- **`level=logging.INFO`** - Shows INFO, WARNING, ERROR, and CRITICAL messages
- **`format='%(message)s'`** - Shows just the message (no timestamp, level name, etc.)

## Log Levels Explained

Python has 5 standard log levels (from lowest to highest):

| Level | Value | When to Use | Will Show? |
|-------|-------|-------------|------------|
| DEBUG | 10 | Detailed diagnostic info | ❌ No (level=INFO) |
| INFO | 20 | General informational messages | ✅ Yes |
| WARNING | 30 | Warning messages | ✅ Yes |
| ERROR | 40 | Error messages | ✅ Yes |
| CRITICAL | 50 | Critical errors | ✅ Yes |

### Why `logger.debug()` Doesn't Show

In your test file (lines 207-209, 215), you used:
```python
logger.debug(f"   ✓ Got details for: {details['title']}")
logger.debug(f"   ✓ Description length: {len(details['description'])} chars")
logger.debug(f"   ✓ Images: {len(details['images'])}")
logger.debug(f"   ✓ Listing available: {available}")
```

Since we set `level=logging.INFO`, DEBUG messages are **filtered out** and won't display.

### To See DEBUG Messages

Change the level to DEBUG:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(message)s'
)
```

Or change your code to use `logger.info()` instead:
```python
logger.info(f"   ✓ Got details for: {details['title']}")
logger.info(f"   ✓ Description length: {len(details['description'])} chars")
```

## Current Output

With `level=logging.INFO`, you see:

```
Running Craigslist Scraper Tests...

1. Testing basic search...
HTTP Request: GET https://sfbay.craigslist.org/search/sss?query=iPhone "HTTP/1.1 200 OK"
   ✓ Found 3 results

2. Testing product details...
HTTP Request: GET https://sfbay.craigslist.org/eby/mob/d/hayward-apple-iphone-16-pro-max-black/7919416536.html "HTTP/1.1 200 OK"

3. Testing availability check...
HTTP Request: GET https://sfbay.craigslist.org/eby/mob/d/hayward-apple-iphone-16-pro-max-black/7919416536.html "HTTP/1.1 200 OK"

✅ All tests passed!
```

Notice:
- ✅ `logger.info()` messages show (lines 196, 199, 201, 205, 213, 218)
- ❌ `logger.debug()` messages don't show (lines 207-209, 215)
- ✅ HTTP requests show (from httpx library, which uses INFO level)

## Better Logging Configuration

For more detailed output, you can use:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
```

This shows:
- Timestamp
- Logger name
- Log level
- Message

Example output:
```
18:14:50 - __main__ - INFO - Running Craigslist Scraper Tests...
18:14:50 - __main__ - INFO - 1. Testing basic search...
18:14:51 - __main__ - INFO -    ✓ Found 3 results
18:14:51 - __main__ - DEBUG -    ✓ Got details for: Apple iPhone 16 Pro Max
```

## Quick Reference

### Basic Setup (Simple)
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("This will show")
logger.debug("This won't show")
```

### Full Setup (Detailed)
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

logger.debug("Detailed diagnostic info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### File Output
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='test.log',  # Write to file instead of console
    filemode='w'  # 'w' = overwrite, 'a' = append
)
```

### Both Console and File
```python
import logging

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(message)s'))

# File handler
file_handler = logging.FileHandler('test.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

## Common Mistakes

### ❌ Mistake 1: No Configuration
```python
logger = logging.getLogger(__name__)
logger.info("This won't show!")  # No output!
```

### ✅ Fix: Add basicConfig
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("This will show!")
```

### ❌ Mistake 2: Wrong Level
```python
logging.basicConfig(level=logging.WARNING)  # Too high!
logger = logging.getLogger(__name__)
logger.info("This won't show!")  # INFO < WARNING
```

### ✅ Fix: Use Appropriate Level
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("This will show!")
```

### ❌ Mistake 3: Using print() Instead
```python
print("Test output")  # Works but not configurable
```

### ✅ Fix: Use Logger
```python
logger.info("Test output")  # Configurable, filterable, better!
```

## Best Practices

1. **Always configure logging** at the start of your script
2. **Use appropriate log levels**:
   - DEBUG: Detailed diagnostic info for debugging
   - INFO: General informational messages
   - WARNING: Something unexpected but not an error
   - ERROR: An error occurred
   - CRITICAL: A serious error, program may not continue

3. **Use logger, not print()** for output in production code
4. **Include context** in log messages:
   ```python
   logger.info(f"Found {len(results)} results for query '{query}'")
   ```

5. **Don't log sensitive data** (passwords, API keys, etc.)

## Summary

Your test file now works because we added:
```python
logging.basicConfig(level=logging.INFO, format='%(message)s')
```

This tells Python:
- ✅ Show INFO level and above
- ✅ Output to console (default)
- ✅ Use simple format (just the message)

To see more detail, change `logger.debug()` to `logger.info()` or change the level to `logging.DEBUG`.
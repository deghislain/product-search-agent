# Selenium ChromeDriver Version Mismatch - Solution

## The Problem

**Error Message:**
```
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: 
This version of ChromeDriver only supports Chrome version 114
Current browser version is 146.0.7680.164
```

**What This Means:**
- Your Chrome browser is version **146** (very new!)
- The ChromeDriver that was downloaded is version **114** (old)
- Selenium requires ChromeDriver version to match Chrome browser version
- They must be compatible to work together

## Why This Happens

The `webdriver-manager` package sometimes:
1. Downloads an outdated ChromeDriver version
2. Caches old versions
3. Doesn't automatically update to match your browser

## Solutions (Try in Order)

### Solution 1: Clear Cache and Force Update (Recommended)

```bash
# Clear webdriver-manager cache
rm -rf ~/.wdm

# Or on Windows:
# rmdir /s %USERPROFILE%\.wdm

# Then run the test again - it will download the correct version
cd backend
uv run python app/tests/test_selenium_setup.py
```

### Solution 2: Use Selenium Manager (Selenium 4.6+)

Selenium now has built-in driver management. Update the test to not use webdriver-manager:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_selenium():
    """Test if Selenium can open Chrome"""
    print("Testing Selenium setup...")
    
    # Configure Chrome options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Let Selenium manage the driver automatically
    driver = webdriver.Chrome(options=options)
    
    # Test by opening Google
    driver.get("https://www.google.com")
    print(f"✓ Successfully opened: {driver.title}")
    
    # Cleanup
    driver.quit()
    print("✓ Selenium setup working!")

if __name__ == "__main__":
    test_selenium()
```

### Solution 3: Manually Specify ChromeDriver Version

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_selenium():
    """Test if Selenium can open Chrome"""
    print("Testing Selenium setup...")
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Force download latest version
    service = Service(ChromeDriverManager(driver_version="latest").install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get("https://www.google.com")
    print(f"✓ Successfully opened: {driver.title}")
    
    driver.quit()
    print("✓ Selenium setup working!")

if __name__ == "__main__":
    test_selenium()
```

### Solution 4: Use Chromium Instead of Chrome

If you have Chromium installed:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_selenium():
    """Test if Selenium can open Chromium"""
    print("Testing Selenium setup with Chromium...")
    
    options = Options()
    options.binary_location = '/usr/bin/chromium-browser'  # Adjust path as needed
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://www.google.com")
    print(f"✓ Successfully opened: {driver.title}")
    
    driver.quit()
    print("✓ Selenium setup working!")

if __name__ == "__main__":
    test_selenium()
```

## Recommended Approach for Your Project

For the Facebook Marketplace scraper, I recommend **Solution 2** (Selenium Manager) because:
- ✅ No external dependencies (webdriver-manager)
- ✅ Automatically manages driver versions
- ✅ Built into Selenium 4.6+
- ✅ Simpler code
- ✅ More reliable

## How to Check Your Chrome Version

### Linux:
```bash
google-chrome --version
# or
chromium-browser --version
```

### Windows:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version
```

### Mac:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

## Understanding the Error

```
Current browser version is 146.0.7680.164 with binary path /usr/sbin/chromium-browser
```

This tells you:
- **Browser version:** 146.0.7680.164
- **Browser location:** /usr/sbin/chromium-browser
- **Browser type:** Chromium (not Chrome)

Since you're using Chromium, you might want to use Solution 4 or ensure the driver matches Chromium.

## Prevention

To avoid this issue in the future:

1. **Use Selenium Manager** (built-in, automatic)
2. **Pin Chrome/Chromium version** (don't auto-update)
3. **Use Docker** (controlled environment)
4. **Regular updates** (keep both browser and driver in sync)

## For Production

In production, consider:
- Using Docker with specific Chrome/ChromeDriver versions
- Using cloud services like BrowserStack or Selenium Grid
- Using headless browsers like Playwright (alternative to Selenium)

## Next Steps

1. Try Solution 1 (clear cache) first
2. If that doesn't work, try Solution 2 (Selenium Manager)
3. Update your Facebook scraper to use the working solution
4. Continue with Day 7 implementation

---

**Note:** This is a common issue when learning Selenium. Don't worry - it's not your fault! Browser and driver version mismatches happen to everyone.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_selenium():
    """Test if Selenium can open Chrome/Chromium"""
    print("Testing Selenium setup...")
    print("Using Selenium Manager (automatic driver management)")
    
    # Configure Chrome options
    options = Options()
    options.add_argument('--headless')  # Run without opening browser window
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Let Selenium Manager handle the driver automatically
    # This works with both Chrome and Chromium
    driver = webdriver.Chrome(options=options)
    
    # Test by opening Google
    driver.get("https://www.google.com")
    print(f"✓ Successfully opened: {driver.title}")
    
    # Cleanup
    driver.quit()
    print("✓ Selenium setup working!")

if __name__ == "__main__":
    test_selenium()
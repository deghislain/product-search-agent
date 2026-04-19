"""Test script to inspect eBay HTML structure"""
import asyncio
import httpx
from bs4 import BeautifulSoup

async def test_ebay_html():
    """Fetch and inspect eBay search results HTML"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    url = "https://www.ebay.com/sch/i.html?_nkw=iPhone+13&_sop=12&_udhi=1000&LH_BIN=1"
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        print("\n" + "="*80)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for different possible item containers
        print("\n1. Looking for 'li.s-item' elements:")
        items = soup.find_all('li', class_='s-item')
        print(f"   Found {len(items)} items")
        
        print("\n2. Looking for 'div.s-item' elements:")
        items = soup.find_all('div', class_='s-item')
        print(f"   Found {len(items)} items")
        
        print("\n3. Looking for any element with 's-item' in class:")
        items = soup.find_all(class_=lambda x: x and 's-item' in x)
        print(f"   Found {len(items)} items")
        
        print("\n4. Looking for 'srp-results' container:")
        results_container = soup.find('ul', class_='srp-results')
        if results_container:
            print(f"   Found srp-results container")
            items = results_container.find_all('li')
            print(f"   Contains {len(items)} <li> elements")
        else:
            print("   No srp-results container found")
        
        # Print first few class names to see structure
        print("\n5. First 10 elements with classes:")
        all_with_class = soup.find_all(class_=True)[:10]
        for i, elem in enumerate(all_with_class, 1):
            print(f"   {i}. <{elem.name}> classes: {elem.get('class')}")
        
        # Save HTML to file for inspection
        with open('ebay_search_results.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("\n✓ Full HTML saved to 'ebay_search_results.html'")

if __name__ == "__main__":
    asyncio.run(test_ebay_html())

# Made with Bob

"""
Debug script to inspect eBay HTML structure
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.scrapers.ebay import EbayScraper
from bs4 import BeautifulSoup


async def debug_ebay():
    scraper = EbayScraper()
    
    # Build URL
    search_url = scraper._build_search_url("iPhone 13")
    print(f"Search URL: {search_url}\n")
    
    # Make request
    response = await scraper._make_request(search_url)
    print(f"Response status: {response.status_code}")
    print(f"Response length: {len(response.text)} characters\n")
    
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all list items
    all_li = soup.find_all('li')
    print(f"Total <li> elements found: {len(all_li)}\n")
    
    # Find s-item class
    s_items = soup.find_all('li', class_='s-item')
    print(f"Items with class 's-item': {len(s_items)}\n")
    
    if s_items:
        print("First s-item structure:")
        print("=" * 60)
        print(s_items[0].prettify()[:1000])
        print("=" * 60)
        print("\nFirst s-item text:")
        print(s_items[0].get_text()[:500])
        print("=" * 60)
    else:
        print("No s-item elements found!")
        print("\nLet's check what classes are actually used:")
        print("=" * 60)
        # Get first 5 li elements and their classes
        for i, li in enumerate(all_li[:5]):
            classes = li.get('class', [])
            print(f"Li {i+1} classes: {classes}")
            if classes:
                print(f"  Text preview: {li.get_text()[:100]}")
        print("=" * 60)
    
    # Save HTML to file for inspection
    with open('backend/ebay_debug.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("\nFull HTML saved to: backend/ebay_debug.html")
    
    await scraper.close()


if __name__ == "__main__":
    asyncio.run(debug_ebay())

# Made with Bob

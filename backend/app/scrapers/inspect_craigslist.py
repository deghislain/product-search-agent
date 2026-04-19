"""
Craigslist HTML Inspector

This script fetches a Craigslist search page and shows you the actual HTML structure
so you can update your CSS selectors.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.craigslist import CraigslistScraper
from bs4 import BeautifulSoup


async def inspect_html():
    """Fetch and inspect Craigslist HTML structure."""
    print("="*60)
    print("Craigslist HTML Structure Inspector")
    print("="*60)
    
    scraper = CraigslistScraper()
    
    try:
        # Build search URL
        search_url = scraper._build_search_url("sfbay", "sss", "iPhone", None, None)
        print(f"\nFetching: {search_url}\n")
        
        # Get the page
        response = await scraper._make_request(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save full HTML to file for inspection
        with open('craigslist_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("✅ Full HTML saved to: craigslist_page.html")
        
        # Look for common result containers
        print("\n" + "="*60)
        print("Looking for result containers...")
        print("="*60)
        
        # Check old structure
        old_results = soup.find_all('li', class_='result-row')
        print(f"\n❌ Old structure (li.result-row): {len(old_results)} found")
        
        # Check for new possible structures
        print("\nSearching for new structures...")
        
        # Try different selectors
        selectors_to_try = [
            ('li', {'class': 'cl-static-search-result'}),
            ('li', {'class': 'result'}),
            ('div', {'class': 'result'}),
            ('div', {'class': 'gallery-card'}),
            ('div', {'class': 'cl-search-result'}),
            ('article', {}),
            ('li', {}),  # Any li
        ]
        
        for tag, attrs in selectors_to_try:
            elements = soup.find_all(tag, attrs) if attrs else soup.find_all(tag)
            if elements and len(elements) > 5:  # Likely to be results if there are many
                print(f"\n✅ Found {len(elements)} <{tag}> elements", end="")
                if attrs:
                    print(f" with {attrs}")
                else:
                    print()
                
                # Show first element structure
                first = elements[0]
                print(f"\nFirst element structure:")
                print(first.prettify()[:500])
                print("...")
                break
        
        # Look for links that might be product URLs
        print("\n" + "="*60)
        print("Looking for product links...")
        print("="*60)
        
        all_links = soup.find_all('a', href=True)
        product_links = [a for a in all_links if '/d/' in a['href'] or 'craigslist.org' in a['href']]
        
        print(f"\nFound {len(product_links)} potential product links")
        if product_links:
            print("\nFirst 5 product links:")
            for i, link in enumerate(product_links[:5], 1):
                print(f"{i}. {link.get('href', 'No href')[:80]}")
                print(f"   Text: {link.get_text(strip=True)[:60]}")
        
        # Look for prices
        print("\n" + "="*60)
        print("Looking for prices...")
        print("="*60)
        
        # Try different price selectors
        price_selectors = [
            ('span', {'class': 'result-price'}),
            ('span', {'class': 'price'}),
            ('div', {'class': 'price'}),
        ]
        
        for tag, attrs in price_selectors:
            prices = soup.find_all(tag, attrs)
            if prices:
                print(f"\n✅ Found {len(prices)} prices with <{tag} {attrs}>")
                print(f"   First price: {prices[0].get_text(strip=True)}")
                break
        
    finally:
        await scraper.close()
    
    print("\n" + "="*60)
    print("Inspection complete!")
    print("Check 'craigslist_page.html' for full HTML")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(inspect_html())

# Made with Bob

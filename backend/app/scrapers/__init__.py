"""
Scrapers Package

Contains all platform-specific scrapers.
"""

from app.scrapers.base import BaseScraper
from app.scrapers.craigslist import CraigslistScraper
from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper

__all__ = [
    'BaseScraper',
    'CraigslistScraper',
    'FacebookMarketplaceScraper',
]
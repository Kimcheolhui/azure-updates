"""
RSS Feed Parser for Azure Updates (Redesigned)
Fetches and parses the Azure updates RSS feed with improved categorization
"""
import feedparser
import sys
import os
from datetime import datetime
from typing import Dict, Optional
from email.utils import parsedate_to_datetime

# Add parent directory to path to import database module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DatabaseManager


class AzureRSSParser:
    """Parser for Azure updates RSS feed"""
    
    RSS_URL = "https://www.microsoft.com/releasecommunications/api/v2/azure/rss"
    
    # Known update type keywords (like Features, Retirements, etc.)
    UPDATE_TYPE_KEYWORDS = {
        'Features', 'Retirements', 'Retirement', 'Compliance',
        'SDK and Tools', 'Services', 'Management', 'Open Source',
        'Microsoft Build', 'Microsoft Ignite'
    }
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the RSS parser
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db_manager = db_manager
    
    def fetch_feed(self, validate: bool = True) -> feedparser.FeedParserDict:
        """
        Fetch the RSS feed from Azure
        
        Args:
            validate: Whether to validate feed was fetched successfully
            
        Returns:
            Parsed RSS feed
            
        Raises:
            RuntimeError: If feed fetch fails and validate is True
        """
        print(f"Fetching RSS feed from {self.RSS_URL}...")
        feed = feedparser.parse(self.RSS_URL)
        
        # Check if parsing had issues
        if hasattr(feed, 'bozo') and feed.bozo:
            print(f"Warning: Feed parsing encountered an error: {getattr(feed, 'bozo_exception', 'Unknown error')}")
        
        # Check HTTP status if available
        status = getattr(feed, 'status', None)
        status_error = status is not None and not (200 <= int(status) < 300)
        
        # Consider it a failure if we have an HTTP error or no entries were returned
        entries = getattr(feed, 'entries', [])
        if validate and (status_error or not entries):
            error_msg = (
                f"Error: Failed to fetch RSS feed. "
                f"HTTP status: {status}, entries fetched: {len(entries)}"
            )
            print(error_msg)
            raise RuntimeError("Failed to fetch Azure RSS feed.")
        
        print(f"Successfully fetched {len(entries)} entries")
        return feed
    
    def parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse date string from RSS feed
        
        Args:
            date_string: Date string from RSS feed
            
        Returns:
            Datetime object or None if parsing fails
        """
        try:
            return parsedate_to_datetime(date_string)
        except (ValueError, TypeError, AttributeError):
            # Return None if parsing fails instead of using current time
            return None
    
    def extract_status_from_categories(self, categories: list) -> str:
        """
        Extract status from RSS categories
        
        Args:
            categories: List of category strings from RSS feed
            
        Returns:
            Status string ('In development', 'In preview', 'Launched')
        """
        # Normalize categories for comparison
        normalized = [cat.strip().lower() for cat in categories]
        
        # Check each status keyword
        for status, keywords in self.db_manager.STATUS_KEYWORDS.items():
            for keyword in keywords:
                if keyword in normalized:
                    return status
        
        # Default to 'Launched' if no status found
        return 'Launched'
    
    def categorize_rss_category(self, category_name: str) -> tuple:
        """
        Categorize an RSS category into product category, product, or update type
        
        Args:
            category_name: Category name from RSS feed
            
        Returns:
            Tuple of (is_product_category, is_product, is_update_type)
        """
        # Check if it's a product category (high-level like Compute, Storage, etc.)
        is_product_category = category_name in self.db_manager.PRODUCT_CATEGORIES
        
        # Check if it's an update type (Features, Retirements, etc.)
        is_update_type = category_name in self.UPDATE_TYPE_KEYWORDS
        
        # Check if it's a status (we handle these separately)
        is_status = any(keyword in category_name.lower() 
                       for keywords in self.db_manager.STATUS_KEYWORDS.values() 
                       for keyword in keywords)
        
        # If it's not a category, update type, or status, it's likely a product
        is_product = not (is_product_category or is_update_type or is_status)
        
        return (is_product_category, is_product, is_update_type)
    
    def parse_and_store_entry(self, entry: Dict) -> bool:
        """
        Parse a single RSS entry and store it in the database
        
        Args:
            entry: RSS feed entry dictionary
            
        Returns:
            True if entry was successfully stored, False otherwise
        """
        try:
            # Extract basic information
            guid = entry.get('id', entry.get('guid', ''))
            link = entry.get('link', '')
            title = entry.get('title', '')
            description = entry.get('description', entry.get('summary', ''))
            
            # Parse dates
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
            elif 'published' in entry:
                pub_date = self.parse_date(entry.published)
            
            # If pub_date is still None, skip this entry
            if pub_date is None:
                print(f"Skipping entry {guid} - no valid publication date")
                return False
            
            updated_date = None
            if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                updated_date = datetime(*entry.updated_parsed[:6])
            elif 'updated' in entry:
                updated_date = self.parse_date(entry.updated)
            
            # Use pub_date if updated_date is None
            if updated_date is None:
                updated_date = pub_date
            
            # Extract categories from tags
            categories = []
            if 'tags' in entry:
                categories = [tag.get('term', '') for tag in entry.tags if tag.get('term', '')]
            
            # Extract status from categories
            status = self.extract_status_from_categories(categories)
            
            # Insert update into database
            update_id = self.db_manager.insert_update(
                guid=guid,
                link=link,
                title=title,
                description=description,
                status=status,
                pub_date=pub_date,
                updated_date=updated_date
            )
            
            if update_id is None:
                print(f"Skipping duplicate entry: {guid}")
                return False
            
            # Process categories and link to appropriate tables
            product_categories_seen = {}  # Track category_name -> category_id
            
            for category_name in categories:
                if not category_name:
                    continue
                
                is_prod_cat, is_product, is_update_type = self.categorize_rss_category(category_name)
                
                if is_prod_cat:
                    # Store product category for later use with products
                    cat_id = self.db_manager.get_or_create_product_category(category_name)
                    if cat_id:
                        product_categories_seen[category_name] = cat_id
                
                elif is_update_type:
                    # Link to update types table
                    update_type_id = self.db_manager.get_or_create_update_type(category_name)
                    self.db_manager.link_update_to_update_type(update_id, update_type_id)
                
                elif is_product:
                    # Determine which product category this product belongs to
                    # Look for a product category that appeared before this product in the categories list
                    product_cat_id = None
                    for cat_name, cat_id in product_categories_seen.items():
                        product_cat_id = cat_id
                        break  # Use the most recent product category
                    
                    # Create product and link to update
                    product_id = self.db_manager.get_or_create_product(category_name, product_cat_id)
                    self.db_manager.link_update_to_product(update_id, product_id)
            
            print(f"Stored update: {title[:50]}...")
            return True
            
        except Exception as e:
            entry_id = entry.get('id', entry.get('guid', 'unknown'))
            entry_title = entry.get('title', 'untitled')[:50]
            import traceback
            print(f"Error parsing entry {entry_id} ('{entry_title}...'): {e}")
            traceback.print_exc()
            return False
    
    def crawl_and_store(self, validate_feed: bool = True) -> int:
        """
        Crawl the RSS feed and store all entries in the database
        
        Args:
            validate_feed: Whether to validate feed fetch was successful
            
        Returns:
            Number of new entries stored
        """
        feed = self.fetch_feed(validate=validate_feed)
        
        new_entries = 0
        for entry in feed.entries:
            if self.parse_and_store_entry(entry):
                new_entries += 1
        
        print(f"\nCrawling completed. Stored {new_entries} new entries.")
        return new_entries


def main():
    """Main function to run the crawler"""
    # Initialize database
    db_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'database',
        'azure_updates.db'
    )
    
    db_manager = DatabaseManager(db_path)
    
    # Initialize database if it doesn't exist
    if not os.path.exists(db_path):
        print("Database not found. Initializing...")
        db_manager.initialize_database()
    
    # Run crawler
    parser = AzureRSSParser(db_manager)
    parser.crawl_and_store()
    
    # Print statistics
    print("\n=== Database Statistics ===")
    stats = db_manager.get_statistics()
    print(f"Total updates: {stats['total_updates']}")
    print(f"Total products: {stats['total_products']}")
    print(f"Total product categories: {stats['total_categories']}")
    print(f"Total update types: {stats['total_update_types']}")
    
    print("\nUpdates by status:")
    for status, count in stats.get('by_status', {}).items():
        print(f"  {status}: {count}")
    
    print("\nMost recent 5 updates:")
    recent_updates = db_manager.get_recent_updates(5)
    for update in recent_updates:
        print(f"  - [{update['status']}] {update['title'][:60]}... ({update['pub_date']})")
    
    db_manager.close()


if __name__ == "__main__":
    main()

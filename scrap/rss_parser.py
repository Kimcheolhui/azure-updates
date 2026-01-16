"""
RSS Feed Parser for Azure Updates
Fetches and parses the Azure updates RSS feed
"""
import feedparser
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path to import database module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DatabaseManager


class AzureRSSParser:
    """Parser for Azure updates RSS feed"""
    
    RSS_URL = "https://www.microsoft.com/releasecommunications/api/v2/azure/rss"
    
    # Known status categories
    STATUS_CATEGORIES = {
        "Launched", "In preview", "In development", "Public Preview",
        "Generally Available", "Retirements", "Retirement"
    }
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the RSS parser
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db_manager = db_manager
    
    def fetch_feed(self) -> feedparser.FeedParserDict:
        """
        Fetch the RSS feed from Azure
        
        Returns:
            Parsed RSS feed
        """
        print(f"Fetching RSS feed from {self.RSS_URL}...")
        feed = feedparser.parse(self.RSS_URL)
        
        if feed.bozo:
            print(f"Warning: Feed parsing encountered an error: {feed.bozo_exception}")
        
        print(f"Successfully fetched {len(feed.entries)} entries")
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
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_string)
        except (ValueError, TypeError, AttributeError):
            # Fallback to current time if parsing fails
            return datetime.now()
    
    def categorize_category(self, category_name: str) -> str:
        """
        Determine the type of category
        
        Args:
            category_name: Name of the category
            
        Returns:
            Category type: 'status', 'service_area', 'service', or 'other'
        """
        # Check if it's a status category
        if any(status.lower() in category_name.lower() for status in self.STATUS_CATEGORIES):
            return 'status'
        
        # If it contains specific service names (with parentheses), it's a service
        if '(' in category_name and ')' in category_name:
            return 'service'
        
        # Check for common service area keywords
        service_areas = [
            'Compute', 'Storage', 'Databases', 'Networking', 'Security',
            'AI + machine learning', 'Analytics', 'Internet of Things',
            'Management and governance', 'Developer tools', 'DevOps',
            'Integration', 'Migration', 'Hybrid + multicloud', 'Identity',
            'Containers', 'Mobile', 'Web'
        ]
        
        if category_name in service_areas:
            return 'service_area'
        
        return 'other'
    
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
            else:
                pub_date = datetime.now()
            
            updated_date = None
            if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                updated_date = datetime(*entry.updated_parsed[:6])
            elif 'updated' in entry:
                updated_date = self.parse_date(entry.updated)
            else:
                updated_date = pub_date
            
            # Insert update into database
            update_id = self.db_manager.insert_update(
                guid=guid,
                link=link,
                title=title,
                description=description,
                pub_date=pub_date,
                updated_date=updated_date
            )
            
            if update_id is None:
                print(f"Skipping duplicate entry: {guid}")
                return False
            
            # Process categories (tags)
            if 'tags' in entry:
                for tag in entry.tags:
                    category_name = tag.get('term', '')
                    if category_name:
                        category_type = self.categorize_category(category_name)
                        category_id = self.db_manager.get_or_create_category(
                            category_name, category_type
                        )
                        self.db_manager.link_update_to_category(update_id, category_id)
            
            print(f"Stored update: {title[:50]}...")
            return True
            
        except Exception as e:
            entry_id = entry.get('id', entry.get('guid', 'unknown'))
            entry_title = entry.get('title', 'untitled')[:50]
            print(f"Error parsing entry {entry_id} ('{entry_title}...'): {e}")
            return False
    
    def crawl_and_store(self) -> int:
        """
        Crawl the RSS feed and store all entries in the database
        
        Returns:
            Number of new entries stored
        """
        feed = self.fetch_feed()
        
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
    new_entries = parser.crawl_and_store()
    
    # Print some statistics
    print("\n=== Statistics ===")
    recent_updates = db_manager.get_recent_updates(5)
    print(f"Total categories: {len(db_manager.get_all_categories())}")
    print(f"\nMost recent 5 updates:")
    for update in recent_updates:
        print(f"  - {update['title'][:60]}... ({update['pub_date']})")
    
    db_manager.close()


if __name__ == "__main__":
    main()

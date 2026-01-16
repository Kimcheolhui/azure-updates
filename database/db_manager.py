"""
Database Manager for Azure Updates
Handles database initialization, connections, and basic operations
"""
import sqlite3
import os
from typing import Optional, List, Tuple
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database connections and operations for Azure Updates"""
    
    def __init__(self, db_path: str = "azure_updates.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """
        Create and return a database connection
        
        Returns:
            SQLite connection object
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
        return self.connection
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self, schema_path: str = "schema.sql"):
        """
        Initialize the database with the schema
        
        Args:
            schema_path: Path to the SQL schema file
        """
        # Read schema file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_schema_path = os.path.join(script_dir, schema_path)
        
        with open(full_schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"Database initialized successfully at {self.db_path}")
    
    def insert_update(self, guid: str, link: str, title: str, description: str,
                     pub_date: datetime, updated_date: datetime) -> int:
        """
        Insert a new update into the database
        
        Args:
            guid: Unique identifier for the update
            link: URL to the update
            title: Title of the update
            description: Description of the update
            pub_date: Publication date
            updated_date: Last updated date
            
        Returns:
            ID of the inserted update, or existing ID if update already exists
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO updates (guid, link, title, description, pub_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (guid, link, title, description, pub_date, updated_date))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Update already exists, return its ID
            cursor.execute("SELECT id FROM updates WHERE guid = ?", (guid,))
            result = cursor.fetchone()
            if result:
                return result[0]
            # This should not happen, but handle gracefully
            return None
    
    def get_or_create_category(self, name: str, category_type: str = 'other') -> int:
        """
        Get category ID or create if it doesn't exist
        
        Args:
            name: Category name
            category_type: Type of category (status, service_area, service, other)
            
        Returns:
            Category ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Try to get existing category
        cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new category
        cursor.execute("""
            INSERT INTO categories (name, category_type)
            VALUES (?, ?)
        """, (name, category_type))
        conn.commit()
        return cursor.lastrowid
    
    def link_update_to_category(self, update_id: int, category_id: int):
        """
        Link an update to a category
        
        Args:
            update_id: ID of the update
            category_id: ID of the category
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO update_categories (update_id, category_id)
                VALUES (?, ?)
            """, (update_id, category_id))
            conn.commit()
        except sqlite3.IntegrityError:
            # Link already exists
            pass
    
    def get_updates_by_category(self, category_name: str) -> List[sqlite3.Row]:
        """
        Get all updates for a specific category
        
        Args:
            category_name: Name of the category to filter by
            
        Returns:
            List of update rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT u.*
            FROM updates u
            JOIN update_categories uc ON u.id = uc.update_id
            JOIN categories c ON uc.category_id = c.id
            WHERE c.name = ?
            ORDER BY u.pub_date DESC
        """, (category_name,))
        
        return cursor.fetchall()
    
    def get_recent_updates(self, limit: int = 50) -> List[sqlite3.Row]:
        """
        Get the most recent updates
        
        Args:
            limit: Maximum number of updates to return
            
        Returns:
            List of update rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM updates
            ORDER BY pub_date DESC
            LIMIT ?
        """, (limit,))
        
        return cursor.fetchall()
    
    def get_all_categories(self) -> List[sqlite3.Row]:
        """
        Get all categories
        
        Returns:
            List of category rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM categories ORDER BY name")
        return cursor.fetchall()


if __name__ == "__main__":
    # Test database initialization
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    print("Database test completed successfully")

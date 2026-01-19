"""
Database Manager for Azure Updates (Redesigned)
Handles database initialization, connections, and basic operations
"""
import sqlite3
import os
from typing import Optional, List
from datetime import datetime
from email.utils import parsedate_to_datetime


class DatabaseManager:
    """Manages SQLite database connections and operations for Azure Updates"""
    
    # Product category mapping (from RSS categories to database enum)
    PRODUCT_CATEGORIES = {
        'AI + machine learning',
        'Analytics',
        'Compute',
        'Containers',
        'Databases',
        'Developer tools',
        'DevOps',
        'Hybrid + multicloud',
        'Identity',
        'Integration',
        'Internet of Things',
        'Management and governance',
        'Migration',
        'Mobile',
        'Networking',
        'Security',
        'Storage',
        'Web'
    }
    
    # Status keywords for identifying status in RSS feed
    STATUS_KEYWORDS = {
        'In development': ['in development', 'private preview'],
        'In preview': ['in preview', 'public preview'],
        'Launched': ['launched', 'generally available', 'ga']
    }
    
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
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
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
                     status: str, pub_date: datetime, updated_date: datetime) -> Optional[int]:
        """
        Insert a new update into the database
        
        Args:
            guid: Unique identifier for the update
            link: URL to the update
            title: Title of the update
            description: Description of the update
            status: Status of the update ('In development', 'In preview', 'Launched')
            pub_date: Publication date
            updated_date: Last updated date
            
        Returns:
            ID of the inserted update, or existing ID if update already exists, or None if error
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO updates (guid, link, title, description, status, pub_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (guid, link, title, description, status, pub_date, updated_date))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Update already exists, return its ID
            cursor.execute("SELECT id FROM updates WHERE guid = ?", (guid,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
    
    def get_or_create_update_type(self, name: str) -> int:
        """
        Get update type ID or create if it doesn't exist
        
        Args:
            name: Update type name (e.g., 'Features', 'Retirements')
            
        Returns:
            Update type ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Try to get existing update type
        cursor.execute("SELECT id FROM update_types WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new update type
        cursor.execute("INSERT INTO update_types (name) VALUES (?)", (name,))
        conn.commit()
        return cursor.lastrowid
    
    def get_or_create_product_category(self, name: str) -> Optional[int]:
        """
        Get product category ID or create if it doesn't exist
        
        Args:
            name: Product category name (must be in PRODUCT_CATEGORIES enum)
            
        Returns:
            Product category ID, or None if name not in enum
        """
        if name not in self.PRODUCT_CATEGORIES:
            return None
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Try to get existing category
        cursor.execute("SELECT id FROM product_categories WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new category
        cursor.execute("INSERT INTO product_categories (name) VALUES (?)", (name,))
        conn.commit()
        return cursor.lastrowid
    
    def get_or_create_product(self, name: str, category_id: Optional[int] = None) -> int:
        """
        Get product ID or create if it doesn't exist
        
        Args:
            name: Product name (e.g., 'Azure Kubernetes Service (AKS)')
            category_id: Optional product category ID
            
        Returns:
            Product ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Try to get existing product
        cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new product
        cursor.execute("""
            INSERT INTO products (name, category_id)
            VALUES (?, ?)
        """, (name, category_id))
        conn.commit()
        return cursor.lastrowid
    
    def link_update_to_product(self, update_id: int, product_id: int):
        """
        Link an update to a product
        
        Args:
            update_id: ID of the update
            product_id: ID of the product
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO update_products (update_id, product_id)
                VALUES (?, ?)
            """, (update_id, product_id))
            conn.commit()
        except sqlite3.IntegrityError:
            # Link already exists
            pass
    
    def link_update_to_update_type(self, update_id: int, update_type_id: int):
        """
        Link an update to an update type
        
        Args:
            update_id: ID of the update
            update_type_id: ID of the update type
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO update_update_types (update_id, update_type_id)
                VALUES (?, ?)
            """, (update_id, update_type_id))
            conn.commit()
        except sqlite3.IntegrityError:
            # Link already exists
            pass
    
    def get_updates_by_product(self, product_name: str, limit: int = 100) -> List[sqlite3.Row]:
        """
        Get all updates for a specific product
        
        Args:
            product_name: Name of the product to filter by
            limit: Maximum number of updates to return
            
        Returns:
            List of update rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT u.*
            FROM updates u
            JOIN update_products up ON u.id = up.update_id
            JOIN products p ON up.product_id = p.id
            WHERE p.name = ?
            ORDER BY u.pub_date DESC
            LIMIT ?
        """, (product_name, limit))
        
        return cursor.fetchall()
    
    def get_updates_by_category(self, category_name: str, limit: int = 100) -> List[sqlite3.Row]:
        """
        Get all updates for a specific product category
        
        Args:
            category_name: Name of the product category to filter by
            limit: Maximum number of updates to return
            
        Returns:
            List of update rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT u.*
            FROM updates u
            JOIN update_products up ON u.id = up.update_id
            JOIN products p ON up.product_id = p.id
            JOIN product_categories pc ON p.category_id = pc.id
            WHERE pc.name = ?
            ORDER BY u.pub_date DESC
            LIMIT ?
        """, (category_name, limit))
        
        return cursor.fetchall()
    
    def get_updates_by_status(self, status: str, limit: int = 100) -> List[sqlite3.Row]:
        """
        Get all updates with a specific status
        
        Args:
            status: Status to filter by ('In development', 'In preview', 'Launched')
            limit: Maximum number of updates to return
            
        Returns:
            List of update rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM updates
            WHERE status = ?
            ORDER BY pub_date DESC
            LIMIT ?
        """, (status, limit))
        
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
    
    def get_all_products(self) -> List[sqlite3.Row]:
        """
        Get all products with their categories
        
        Returns:
            List of product rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, pc.name as category_name
            FROM products p
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            ORDER BY pc.name, p.name
        """)
        return cursor.fetchall()
    
    def get_all_product_categories(self) -> List[sqlite3.Row]:
        """
        Get all product categories
        
        Returns:
            List of category rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM product_categories ORDER BY name")
        return cursor.fetchall()
    
    def get_all_update_types(self) -> List[sqlite3.Row]:
        """
        Get all update types
        
        Returns:
            List of update type rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM update_types ORDER BY name")
        return cursor.fetchall()
    
    def get_statistics(self) -> dict:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as count FROM updates")
        stats['total_updates'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM product_categories")
        stats['total_categories'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM update_types")
        stats['total_update_types'] = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM updates
            GROUP BY status
        """)
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        return stats


if __name__ == "__main__":
    # Test database initialization
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    print("Database test completed successfully")

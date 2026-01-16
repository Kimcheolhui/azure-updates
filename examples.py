"""
Example queries for Azure Updates Database
Demonstrates how to query and filter updates
"""
import sys
import os

# Add parent directory to path to import database module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DatabaseManager


def main():
    """Run example queries"""
    
    # Initialize database
    db_path = os.path.join(
        os.path.dirname(__file__),
        'database',
        'azure_updates.db'
    )
    
    db = DatabaseManager(db_path)
    
    print("=" * 80)
    print("Azure Updates Database - Example Queries")
    print("=" * 80)
    
    # 1. Get recent updates
    print("\n1. Most Recent 5 Updates:")
    print("-" * 80)
    recent = db.get_recent_updates(5)
    for update in recent:
        print(f"Title: {update['title']}")
        print(f"Date: {update['pub_date']}")
        print(f"Link: {update['link']}")
        print()
    
    # 2. Get all categories by type
    print("\n2. Categories by Type:")
    print("-" * 80)
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category_type, COUNT(*) as count 
        FROM categories 
        GROUP BY category_type 
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"{row['category_type']}: {row['count']} categories")
    
    # 3. Get updates for a specific service
    print("\n3. Updates for 'Azure Kubernetes Service (AKS)':")
    print("-" * 80)
    aks_updates = db.get_updates_by_category("Azure Kubernetes Service (AKS)")
    print(f"Found {len(aks_updates)} updates")
    for update in aks_updates[:3]:
        print(f"- {update['title'][:70]}...")
    
    # 4. Get status-based updates (e.g., retirements)
    print("\n4. Retirement Announcements:")
    print("-" * 80)
    retirements = db.get_updates_by_category("Retirements")
    print(f"Found {len(retirements)} retirement announcements")
    for update in retirements[:3]:
        print(f"- {update['title']}")
    
    # 5. Get updates by service area
    print("\n5. Compute Service Area Updates (last 3):")
    print("-" * 80)
    compute_updates = db.get_updates_by_category("Compute")
    for update in compute_updates[:3]:
        print(f"- {update['title'][:70]}...")
    
    # 6. Get all service categories
    print("\n6. Available Service Categories:")
    print("-" * 80)
    cursor.execute("""
        SELECT DISTINCT name 
        FROM categories 
        WHERE category_type = 'service'
        ORDER BY name
    """)
    services = cursor.fetchall()
    for service in services:
        print(f"- {service['name']}")
    
    # 7. Count updates per status
    print("\n7. Updates by Status:")
    print("-" * 80)
    cursor.execute("""
        SELECT c.name, COUNT(DISTINCT uc.update_id) as count
        FROM categories c
        JOIN update_categories uc ON c.id = uc.category_id
        WHERE c.category_type = 'status'
        GROUP BY c.name
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"{row['name']}: {row['count']} updates")
    
    db.close()
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

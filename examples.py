"""
Example queries for Azure Updates Database
Demonstrates how to query and filter updates
"""
import os
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
    print("\n2. Database Statistics:")
    print("-" * 80)
    stats = db.get_statistics()
    print(f"Total products: {stats['total_products']}")
    print(f"Total product categories: {stats['total_categories']}")
    print(f"Total update types: {stats['total_update_types']}")
    print("\nUpdates by status:")
    for status, count in stats.get('by_status', {}).items():
        print(f"  {status}: {count}")
    
    # 3. Get updates for a specific product
    print("\n3. Updates for 'Azure Kubernetes Service (AKS)':")
    print("-" * 80)
    aks_updates = db.get_updates_by_product("Azure Kubernetes Service (AKS)", limit=10)
    print(f"Found {len(aks_updates)} updates")
    for update in aks_updates[:3]:
        print(f"- [{update['status']}] {update['title'][:60]}...")
    
    # 4. Get updates by status
    print("\n4. Updates 'In preview':")
    print("-" * 80)
    in_preview = db.get_updates_by_status("In preview", limit=5)
    print(f"Found {len(in_preview)} updates in preview")
    for update in in_preview[:3]:
        print(f"- {update['title'][:70]}...")
    
    # 5. Get updates by product category
    print("\n5. Compute Product Category Updates (last 3):")
    print("-" * 80)
    compute_updates = db.get_updates_by_category("Compute", limit=3)
    for update in compute_updates:
        print(f"- [{update['status']}] {update['title'][:60]}...")
    
    # 6. Get all products
    print("\n6. Sample Products (first 10):")
    print("-" * 80)
    products = db.get_all_products()
    for product in products[:10]:
        category = product['category_name'] if product['category_name'] else 'Uncategorized'
        print(f"- {product['name']} ({category})")
    
    # 7. Get all product categories
    print("\n7. All Product Categories:")
    print("-" * 80)
    categories = db.get_all_product_categories()
    for cat in categories:
        print(f"- {cat['name']}")
    
    # 8. Get all update types
    print("\n8. All Update Types:")
    print("-" * 80)
    update_types = db.get_all_update_types()
    for ut in update_types:
        print(f"- {ut['name']}")
    
    db.close()
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

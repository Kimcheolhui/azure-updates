# Database Module

This module manages the SQLite database for storing Azure updates information.

## Database Schema

The database schema has been redesigned to accurately reflect the structure of Azure updates.

### Tables

#### `updates`
Stores the main update information from Azure RSS feed.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| guid | TEXT | Unique identifier from RSS feed (unique) |
| link | TEXT | URL to the Azure update page |
| title | TEXT | Title of the update |
| description | TEXT | Description of the update |
| status | TEXT | Update status: 'In development', 'In preview', 'Launched' (CHECK constraint) |
| pub_date | TIMESTAMP | Publication date |
| updated_date | TIMESTAMP | Last updated date |
| created_at | TIMESTAMP | Record creation timestamp |

#### `product_categories`
Stores high-level Azure product categories (enforced as ENUM via CHECK constraint).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| name | TEXT | Category name (e.g., 'Compute', 'Storage', 'Databases') |
| created_at | TIMESTAMP | Record creation timestamp |

Supported categories: AI + machine learning, Analytics, Compute, Containers, Databases, Developer tools, DevOps, Hybrid + multicloud, Identity, Integration, Internet of Things, Management and governance, Migration, Mobile, Networking, Security, Storage, Web

#### `products`
Stores specific Azure products/services.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| name | TEXT | Product name (e.g., 'Azure Kubernetes Service (AKS)') |
| category_id | INTEGER | Foreign key to product_categories (nullable) |
| created_at | TIMESTAMP | Record creation timestamp |

#### `update_types`
Stores update type information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| name | TEXT | Update type (e.g., 'Features', 'Retirements', 'Compliance') |
| created_at | TIMESTAMP | Record creation timestamp |

#### `update_products`
Junction table for many-to-many relationship between updates and products.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| update_id | INTEGER | Foreign key to updates table |
| product_id | INTEGER | Foreign key to products table |
| created_at | TIMESTAMP | Record creation timestamp |

#### `update_update_types`
Junction table for many-to-many relationship between updates and update types.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| update_id | INTEGER | Foreign key to updates table |
| update_type_id | INTEGER | Foreign key to update_types table |
| created_at | TIMESTAMP | Record creation timestamp |

## Usage

### Initialize Database

```python
from database.db_manager import DatabaseManager

# Create database manager
db = DatabaseManager("azure_updates.db")

# Initialize database with schema
db.initialize_database()
```

### Insert Update

```python
from datetime import datetime

# Insert an update
update_id = db.insert_update(
    guid="536550",
    link="https://azure.microsoft.com/updates?id=536550",
    title="[Launched] Generally Available: Ubuntu 24.04 support in AKS",
    description="Ubuntu 24.04 is now generally available on AKS...",
    status="Launched",  # Status is an enum: 'In development', 'In preview', 'Launched'
    pub_date=datetime.now(),
    updated_date=datetime.now()
)
```

### Work with Products and Categories

```python
# Get or create product category
category_id = db.get_or_create_product_category("Compute")

# Get or create product
product_id = db.get_or_create_product(
    "Azure Kubernetes Service (AKS)", 
    category_id=category_id
)

# Link update to product
db.link_update_to_product(update_id, product_id)

# Create update type
update_type_id = db.get_or_create_update_type("Features")

# Link update to update type
db.link_update_to_update_type(update_id, update_type_id)
```

### Query Updates

```python
# Get updates by product
aks_updates = db.get_updates_by_product("Azure Kubernetes Service (AKS)", limit=10)

# Get updates by product category
compute_updates = db.get_updates_by_category("Compute", limit=20)

# Get updates by status
in_preview = db.get_updates_by_status("In preview", limit=50)

# Get recent updates
recent = db.get_recent_updates(limit=10)

# Get all products with their categories
products = db.get_all_products()

# Get statistics
stats = db.get_statistics()
print(f"Total updates: {stats['total_updates']}")
print(f"By status: {stats['by_status']}")
```

## Design Rationale

The schema redesign addresses the following requirements:

1. **Status as Column**: Status is stored directly in the updates table with a CHECK constraint, treating it as an enum rather than a separate table.

2. **Product Hierarchies**: Product categories (e.g., Compute, Storage) are stored separately from products (e.g., AKS, Azure Files), with products linked to their parent category.

3. **Many-to-Many Relationships**: Updates can have multiple products and update types, handled through junction tables.

4. **Update Types**: Separate table for update types like "Features", "Retirements", "Compliance", etc.

## Migration to Cloud Database

The current implementation uses SQLite for simplicity and local development. When ready to deploy to production, the database can be migrated to:

- **Azure SQL Database**: For relational data with full SQL Server features
- **Azure Cosmos DB**: For global distribution and multi-model support
- **Azure Database for PostgreSQL**: For open-source PostgreSQL compatibility

The `DatabaseManager` class is designed with a clean interface that can be extended or replaced with cloud-specific implementations.

## Files

- `schema.sql`: SQL schema definition
- `db_manager.py`: Database manager class with CRUD operations
- `README.md`: This documentation file

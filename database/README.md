# Database Module

This module manages the SQLite database for storing Azure updates information.

## Database Schema

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
| pub_date | TIMESTAMP | Publication date |
| updated_date | TIMESTAMP | Last updated date |
| created_at | TIMESTAMP | Record creation timestamp |

#### `categories`
Stores unique categories extracted from RSS feed.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| name | TEXT | Category name (unique) |
| category_type | TEXT | Type: 'status', 'service_area', 'service', 'other' |
| created_at | TIMESTAMP | Record creation timestamp |

#### `update_categories`
Junction table for many-to-many relationship between updates and categories.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| update_id | INTEGER | Foreign key to updates table |
| category_id | INTEGER | Foreign key to categories table |
| created_at | TIMESTAMP | Record creation timestamp |

## Usage

### Initialize Database

```python
from db_manager import DatabaseManager

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
    pub_date=datetime(2026, 1, 14, 22, 45, 12),
    updated_date=datetime(2026, 1, 14, 22, 45, 12)
)
```

### Work with Categories

```python
# Create or get category
category_id = db.get_or_create_category("Azure Kubernetes Service (AKS)", "service")

# Link update to category
db.link_update_to_category(update_id, category_id)
```

### Query Updates

```python
# Get updates by category
updates = db.get_updates_by_category("Azure Kubernetes Service (AKS)")

# Get recent updates
recent = db.get_recent_updates(limit=10)

# Get all categories
categories = db.get_all_categories()
```

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

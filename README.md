# Azure Updates Notification System

A service that monitors Azure updates and sends email notifications for updates relevant to specific Solution Areas or services.

## Overview

This project crawls Azure update announcements from Microsoft's RSS feed and stores them in a database. The system is designed as a monorepo with separate modules for different functionalities:

- **Database**: Schema and database management utilities
- **Scrap (Crawler)**: RSS feed parser and crawler
- **Mail** (Coming soon): Email notification service

## Azure Updates Source

Azure publishes updates, new features, and retirements at:
- **Web**: https://azure.microsoft.com/en-us/updates
- **RSS Feed**: https://www.microsoft.com/releasecommunications/api/v2/azure/rss

## Project Structure

```
azure-updates/
├── database/           # Database schema and management
│   ├── schema.sql     # SQLite database schema
│   ├── db_manager.py  # Database manager class
│   └── README.md      # Database documentation
├── scrap/             # RSS crawler and parser
│   ├── rss_parser.py  # RSS feed crawler
│   └── README.md      # Crawler documentation
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Kimcheolhui/azure-updates.git
cd azure-updates
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
cd database
python db_manager.py
```

4. Run the crawler:
```bash
cd ../scrap
python rss_parser.py
```

## Usage

### Crawling Azure Updates

The crawler fetches the latest updates from the Azure RSS feed and stores them in the database:

```bash
cd scrap
python rss_parser.py
```

This will:
- Fetch all entries from the RSS feed
- Parse and categorize each update
- Store new updates in the database
- Skip duplicates automatically
- Display statistics

### Database Operations

You can interact with the database programmatically:

```python
from database.db_manager import DatabaseManager

# Initialize database manager
db = DatabaseManager("database/azure_updates.db")

# Get recent updates
recent = db.get_recent_updates(limit=10)
for update in recent:
    print(f"{update['title']} - {update['pub_date']}")

# Get updates by category
aks_updates = db.get_updates_by_category("Azure Kubernetes Service (AKS)")

# Get all categories
categories = db.get_all_categories()
```

## Database Schema

The system uses SQLite with three main tables:

- **updates**: Stores Azure update information (guid, title, description, dates, etc.)
- **categories**: Stores unique categories (status, service areas, services)
- **update_categories**: Links updates to their categories (many-to-many)

For detailed schema information, see [database/README.md](database/README.md).

## Features

### Current Features
- ✅ RSS feed crawling and parsing
- ✅ SQLite database with normalized schema
- ✅ Automatic category classification (status, service area, service)
- ✅ Duplicate detection
- ✅ Query API for filtering updates by category
- ✅ Documentation for all modules

### Planned Features
- 📧 Email notification service
- 🔍 User subscription management
- 🎯 Custom filtering based on solution areas
- ☁️ Cloud database migration (Azure SQL, Cosmos DB, or PostgreSQL)
- ⏰ Scheduled crawling (via Azure Functions or GitHub Actions)
- 🔔 Webhook support for real-time notifications

## Technology Stack

- **Language**: Python 3
- **Database**: SQLite (for development, easily migrated to cloud DB)
- **RSS Parser**: feedparser library
- **Future**: Azure Functions, SendGrid/Azure Communication Services for email

## Cloud Migration Path

The current SQLite implementation is designed for easy migration to cloud databases:

- **Azure SQL Database**: Full SQL Server compatibility
- **Azure Cosmos DB**: Global distribution, multi-model
- **Azure Database for PostgreSQL**: Open-source option

The `DatabaseManager` class interface remains the same, only the connection logic needs updating.

## Contributing

This project is structured as a monorepo for easier development and deployment. Each module (database, scrap, mail) is independent but shares the common database layer.

## License

[Add your license here]

## Contact

[Add contact information]

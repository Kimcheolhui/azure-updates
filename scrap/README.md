# Scraper/Crawler Module

This module handles the crawling and parsing of Azure updates from the RSS feed.

## Overview

The scraper fetches Azure updates from the Microsoft RSS feed and stores them in the database. It automatically categorizes updates based on their tags and handles duplicate entries.

## RSS Feed

**URL**: https://www.microsoft.com/releasecommunications/api/v2/azure/rss

The feed provides:
- Update announcements (Launched, In Preview, In Development)
- Service retirements and deprecations
- New features and capabilities
- Regional availability updates

## Usage

### Basic Crawling

```python
from rss_parser import AzureRSSParser
from database.db_manager import DatabaseManager

# Initialize database manager
db = DatabaseManager("../database/azure_updates.db")

# Create parser
parser = AzureRSSParser(db)

# Crawl and store updates
new_entries = parser.crawl_and_store()
print(f"Stored {new_entries} new updates")
```

### Run from Command Line

```bash
cd scrap
python rss_parser.py
```

This will:
1. Fetch the latest updates from the RSS feed
2. Parse each entry
3. Store new updates in the database
4. Skip duplicate entries
5. Display statistics

## Category Classification

The parser automatically classifies categories into types:

### Status Categories
Updates about the state of features:
- "Launched"
- "In preview" / "Public Preview"
- "In development"
- "Generally Available"
- "Retirements" / "Retirement"

### Service Area Categories
High-level Azure service areas:
- Compute
- Storage
- Databases
- Networking
- Security
- AI + machine learning
- Analytics
- Internet of Things
- And more...

### Service Categories
Specific Azure services (usually in parentheses):
- Azure Kubernetes Service (AKS)
- Azure SQL Database
- Azure Cosmos DB
- Azure Functions
- And more...

## Features

- **Duplicate Detection**: Automatically skips entries that are already in the database
- **Automatic Categorization**: Classifies categories by type for better filtering
- **Error Handling**: Continues processing even if individual entries fail
- **Progress Reporting**: Shows real-time progress during crawling
- **Statistics**: Displays summary after completion

## Dependencies

- `feedparser`: For parsing RSS feeds
- `sqlite3`: For database operations (built-in)

## Scheduled Crawling

For production use, you can schedule regular crawling using:

### Option 1: Cron (Linux/Mac)
```bash
# Run every hour
0 * * * * cd /path/to/azure-updates/scrap && python rss_parser.py
```

### Option 2: Azure Functions
Deploy the crawler as a timer-triggered Azure Function for serverless execution.

### Option 3: GitHub Actions
Use GitHub Actions workflow to run the crawler on a schedule.

## Files

- `rss_parser.py`: Main RSS parser and crawler implementation
- `README.md`: This documentation file

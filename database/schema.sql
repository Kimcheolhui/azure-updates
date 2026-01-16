-- Azure Updates Database Schema

-- Table: updates
-- Stores the main update information from Azure RSS feed
CREATE TABLE IF NOT EXISTS updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    link TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    pub_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(guid)
);

-- Table: categories
-- Stores unique categories (status, service area, specific service)
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category_type TEXT, -- 'status', 'service_area', 'service', 'other'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: update_categories
-- Junction table for many-to-many relationship between updates and categories
CREATE TABLE IF NOT EXISTS update_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (update_id) REFERENCES updates(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE(update_id, category_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_updates_pub_date ON updates(pub_date DESC);
CREATE INDEX IF NOT EXISTS idx_updates_guid ON updates(guid);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_update_categories_update_id ON update_categories(update_id);
CREATE INDEX IF NOT EXISTS idx_update_categories_category_id ON update_categories(category_id);

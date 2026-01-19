-- Azure Updates Database Schema (Redesigned)
-- Based on actual Azure Updates website structure

-- Table: updates
-- Stores the main update information from Azure RSS feed
CREATE TABLE IF NOT EXISTS updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    link TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK(status IN ('In development', 'In preview', 'Launched')), -- Status as ENUM-like constraint
    pub_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: update_types
-- Stores update type information (e.g., Features, Compliance, Retirements, etc.)
CREATE TABLE IF NOT EXISTS update_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL, -- e.g., 'Features', 'Retirements', 'Compliance', 'SDK and Tools', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: product_categories
-- Stores high-level product categories (e.g., Compute, Storage, Databases, Networking)
CREATE TABLE IF NOT EXISTS product_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL CHECK(name IN (
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
    )),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: products
-- Stores specific Azure products/services
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL, -- e.g., 'Azure Kubernetes Service (AKS)', 'Azure SQL Database'
    category_id INTEGER, -- Foreign key to product_categories (can be NULL for uncategorized products)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(id) ON DELETE SET NULL
);

-- Table: update_products
-- Junction table for many-to-many relationship between updates and products
CREATE TABLE IF NOT EXISTS update_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (update_id) REFERENCES updates(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(update_id, product_id)
);

-- Table: update_update_types
-- Junction table for many-to-many relationship between updates and update_types
CREATE TABLE IF NOT EXISTS update_update_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_id INTEGER NOT NULL,
    update_type_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (update_id) REFERENCES updates(id) ON DELETE CASCADE,
    FOREIGN KEY (update_type_id) REFERENCES update_types(id) ON DELETE CASCADE,
    UNIQUE(update_id, update_type_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_updates_pub_date ON updates(pub_date DESC);
CREATE INDEX IF NOT EXISTS idx_updates_guid ON updates(guid);
CREATE INDEX IF NOT EXISTS idx_updates_status ON updates(status);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_update_products_update_id ON update_products(update_id);
CREATE INDEX IF NOT EXISTS idx_update_products_product_id ON update_products(product_id);
CREATE INDEX IF NOT EXISTS idx_update_update_types_update_id ON update_update_types(update_id);
CREATE INDEX IF NOT EXISTS idx_update_update_types_update_type_id ON update_update_types(update_type_id);

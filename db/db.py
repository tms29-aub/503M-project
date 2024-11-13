import sqlite3

conn = sqlite3.connect("db\\instance\\503M.db")
conn.execute("PRAGMA foreign_keys = 1")
cursor = conn.cursor()

# Admin
cursor.execute("""
CREATE TABLE IF NOT EXISTS Admin (
    admin_id INTEGER PRIMARY KEY,
    name TEXT,
    phone INTEGER,
    email TEXT,
    hashed_password TEXT
);
""")

# AdminRole
cursor.execute("""
CREATE TABLE IF NOT EXISTS AdminRole (
    admin_role_id INTEGER PRIMARY KEY,
    admin_id INTEGER,
    inventory_management BOOLEAN,
    order_management BOOLEAN,
    product_management BOOLEAN,
    customer_management BOOLEAN,
    customer_support BOOLEAN,
    logs BOOLEAN,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id)
);
""")

# Log
cursor.execute("""
CREATE TABLE IF NOT EXISTS Log (
    log_id INTEGER PRIMARY KEY,
    admin_id INTEGER,
    details TEXT,
    action TEXT,
    timestamp TEXT,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id)
);
""")

# Customer
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customer (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone INTEGER,
    address TEXT,
    tier TEXT CHECK (tier IN ('normal', 'premium', 'gold'))
);
""")

# Support
cursor.execute("""
CREATE TABLE IF NOT EXISTS Support (
    ticket_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    issue_description TEXT,
    status TEXT CHECK (status IN ('open', 'closed')),
    created_at TEXT,
    resolved_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);
""")

# Wishlist
cursor.execute("""
CREATE TABLE IF NOT EXISTS Wishlist (
    wishlist_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);
""")

# ProductCategory
cursor.execute("""
CREATE TABLE IF NOT EXISTS ProductCategory (
    category_id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT
);
""")

# Product
cursor.execute("""
CREATE TABLE IF NOT EXISTS Product (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER,
    name TEXT,
    description TEXT,
    subcategory TEXT,
    price REAL,
    quantity_in_stock INTEGER,
    reorder_level INTEGER,
    image TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (category_id) REFERENCES ProductCategory(category_id)
);
""")

# Report
cursor.execute("""
CREATE TABLE IF NOT EXISTS Report (
    report_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    report_date TEXT,
    turnover_rate REAL,
    demand_forecast INTEGER,
    most_popular TEXT,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);
""")

# Order
cursor.execute("""
CREATE TABLE IF NOT EXISTS "Order" (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    status TEXT CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    total_amount REAL,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);
""")

# OrderItem
cursor.execute("""
CREATE TABLE IF NOT EXISTS OrderItem (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price_at_purchase REAL,
    FOREIGN KEY (order_id) REFERENCES "Order"(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);
""")



# Return
cursor.execute("""
CREATE TABLE IF NOT EXISTS Return (
    return_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    replaced_order_id INTEGER,
    return_reason TEXT,
    status TEXT CHECK (status IN ('pending', 'complete')),
    created_at TEXT,
    FOREIGN KEY (order_id) REFERENCES "Order"(order_id),
    FOREIGN KEY (replaced_order_id) REFERENCES "Order"(order_id)
);
""")





conn.commit()
conn.close()
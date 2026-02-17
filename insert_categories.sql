-- SQL script to insert categories into the database
INSERT OR IGNORE INTO vendor_category (name, description, is_active, created_at) VALUES
('Dairy, Bread & Eggs', 'Dairy, Bread & Eggs products', 1, datetime('now')),
('Fruits & Vegetables', 'Fruits & Vegetables products', 1, datetime('now')),
('Cold Drinks & Juices', 'Cold Drinks & Juices products', 1, datetime('now')),
('Snacks & Munchies', 'Snacks & Munchies products', 1, datetime('now')),
('Breakfast & Instant Food', 'Breakfast & Instant Food products', 1, datetime('now')),
('Sweet Tooth', 'Sweet Tooth products', 1, datetime('now')),
('Bakery & Biscuits', 'Bakery & Biscuits products', 1, datetime('now')),
('Tea, Coffee & Milk Drinks', 'Tea, Coffee & Milk Drinks products', 1, datetime('now')),
('Atta, Rice & Dal', 'Atta, Rice & Dal products', 1, datetime('now')),
('Masala, Oil & More', 'Masala, Oil & More products', 1, datetime('now')),
('Sauces & Spreads', 'Sauces & Spreads products', 1, datetime('now')),
('Chicken, Meat & Fish', 'Chicken, Meat & Fish products', 1, datetime('now')),
('Organic & Healthy Living', 'Organic & Healthy Living products', 1, datetime('now')),
('Baby Care', 'Baby Care products', 1, datetime('now')),
('Pharma & Wellness', 'Pharma & Wellness products', 1, datetime('now')),
('Cleaning Essentials', 'Cleaning Essentials products', 1, datetime('now')),
('Home & Office', 'Home & Office products', 1, datetime('now')),
('Personal Care', 'Personal Care products', 1, datetime('now')),
('Pet Care', 'Pet Care products', 1, datetime('now'));

SELECT COUNT(*) as total_categories FROM vendor_category;

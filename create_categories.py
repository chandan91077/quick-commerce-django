import sqlite3
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check existing categories
cursor.execute("SELECT COUNT(*) FROM vendor_category")
existing_count = cursor.fetchone()[0]
print(f"Existing categories: {existing_count}")

if existing_count == 0:
    print("\nCreating categories...")
    
    categories = [
        'Dairy, Bread & Eggs',
        'Fruits & Vegetables',
        'Cold Drinks & Juices',
        'Snacks & Munchies',
        'Breakfast & Instant Food',
        'Sweet Tooth',
        'Bakery & Biscuits',
        'Tea, Coffee & Milk Drinks',
        'Atta, Rice & Dal',
        'Masala, Oil & More',
        'Sauces & Spreads',
        'Chicken, Meat & Fish',
        'Organic & Healthy Living',
        'Baby Care',
        'Pharma & Wellness',
        'Cleaning Essentials',
        'Home & Office',
        'Personal Care',
        'Pet Care',
    ]
    
    now = datetime.now().isoformat()
    
    for cat_name in categories:
        cursor.execute("""
            INSERT INTO vendor_category (name, description, is_active, created_at)
            VALUES (?, ?, ?, ?)
        """, (cat_name, f'{cat_name} products', 1, now))
        print(f"  ✓ Created: {cat_name}")
    
    conn.commit()
    print(f"\n✅ Created {len(categories)} categories successfully!")
else:
    print("\nCategories already exist:")
    cursor.execute("SELECT name, is_active FROM vendor_category")
    for name, is_active in cursor.fetchall():
        status = "✓" if is_active else "✗"
        print(f"  {status} {name}")

# Final count
cursor.execute("SELECT COUNT(*) FROM vendor_category")
total = cursor.fetchone()[0]
print(f"\nTotal categories in database: {total}")

conn.close()

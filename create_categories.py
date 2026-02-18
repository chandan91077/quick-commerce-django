import os

import django


def create_categories():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finalproject.settings")
    django.setup()

    from vendor.models import Category

    categories = [
        "Dairy, Bread & Eggs",
        "Fruits & Vegetables",
        "Cold Drinks & Juices",
        "Snacks & Munchies",
        "Breakfast & Instant Food",
        "Sweet Tooth",
        "Bakery & Biscuits",
        "Tea, Coffee & Milk Drinks",
        "Atta, Rice & Dal",
        "Masala, Oil & More",
        "Sauces & Spreads",
        "Chicken, Meat & Fish",
        "Organic & Healthy Living",
        "Baby Care",
        "Pharma & Wellness",
        "Cleaning Essentials",
        "Home & Office",
        "Personal Care",
        "Pet Care",
    ]

    existing_count = Category.objects.count()
    print(f"Existing categories: {existing_count}")
    print("\nCreating categories...")

    created_count = 0
    for category_name in categories:
        _, created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                "description": f"{category_name} products",
                "is_active": True,
            },
        )
        if created:
            created_count += 1
            print(f"  ✓ Created: {category_name}")
        else:
            print(f"  - Already exists: {category_name}")

    total = Category.objects.count()
    print(f"\nCreated in this run: {created_count}")
    print(f"Total categories in database: {total}")


if __name__ == "__main__":
    create_categories()

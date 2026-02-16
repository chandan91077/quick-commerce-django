from django.core.management.base import BaseCommand
from vendor.models import Category


class Command(BaseCommand):
    help = 'Create sample product categories'

    def handle(self, *args, **kwargs):
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

        created_count = 0
        for category_name in categories:
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'is_active': True}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(f'Category already exists: {category_name}')

        self.stdout.write(self.style.SUCCESS(f'\nTotal categories created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total categories in database: {Category.objects.count()}'))

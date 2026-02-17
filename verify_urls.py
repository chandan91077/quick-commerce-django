import os
import django
from django.urls import reverse, resolve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalproject.settings')
django.setup()

def verify_urls():
    urls_to_check = [
        'view_cart',
        'checkout', 
        'process_checkout',
        'user_orders'
    ]
    
    print("Verifying URLs...")
    for url_name in urls_to_check:
        try:
            path = reverse(url_name)
            print(f"✅ {url_name} -> {path}")
        except Exception as e:
            print(f"❌ {url_name} -> Error: {e}")

    # Check dynamic URLs with dummy IDs
    dynamic_urls = [
        ('add_to_cart', {'product_id': 1}),
        ('update_cart_item', {'item_id': 1, 'action': 'increment'}),
        ('remove_from_cart', {'item_id': 1})
    ]
    
    for url_name, kwargs in dynamic_urls:
        try:
            path = reverse(url_name, kwargs=kwargs)
            print(f"✅ {url_name} ({kwargs}) -> {path}")
        except Exception as e:
            print(f"❌ {url_name} ({kwargs}) -> Error: {e}")

if __name__ == "__main__":
    verify_urls()

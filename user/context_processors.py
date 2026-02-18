from .models import Cart
import re


def _parse_pincode_list(raw_value):
    if not raw_value:
        return set()
    return set(re.findall(r'\d{6}', str(raw_value)))

def cart_count(request):
    """
    Context processor to make cart count available in all templates.
    """
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            # Count total quantity of items, or just number of unique items?
            # Usually total quantity is better for "items in cart" badge
            count = cart.items.count() 
        except Cart.DoesNotExist:
            count = 0

    delivery_pincode = request.session.get('delivery_pincode', '').strip()
    delivery_available = False

    if delivery_pincode:
        from vendor.models import Vendor
        for vendor_pincode in Vendor.objects.filter(status='approved').values_list('pincode', flat=True):
            if delivery_pincode in _parse_pincode_list(vendor_pincode):
                delivery_available = True
                break

    return {
        'cart_count': count,
        'delivery_pincode': delivery_pincode,
        'delivery_available': delivery_available,
        'delivery_checked': bool(delivery_pincode),
    }

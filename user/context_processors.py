from .models import Cart

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
    return {'cart_count': count}

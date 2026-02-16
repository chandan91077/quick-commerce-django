# Vendor context processor - adds vendor data to template context

def user_vendor_status(request):
    # check if user is vendor
    context = {
        'is_vendor': False,
        'vendor_approved': False,
        'vendor_profile': None,
    }
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'vendor_profile'):
            vendor = request.user.vendor_profile
            context['is_vendor'] = True
            context['vendor_approved'] = vendor.status == 'approved'
            context['vendor_profile'] = vendor
    
    return context

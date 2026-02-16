# Vendor Product Management System

## Overview

The vendor product management system allows vendors to register and manage their products. Vendors can add, edit, and delete products within different categories.

## Features

- **Vendor Dashboard**: View all products added by the vendor
- **Add Products**: Register new products with details like name, category, price, quantity, and image
- **Edit Products**: Update existing product information
- **Delete Products**: Remove products from the listing
- **Product Categories**: Pre-defined categories for organizing products
- **Product Status**: Mark products as active or inactive

## Available Product Categories

1. **Dairy & Eggs** - Fresh dairy products and eggs
2. **Fruits & Vegetables** - Fresh fruits and vegetables
3. **Snacks & Bakery** - Snacks, biscuits, and bakery items
4. **Beverages** - Drinks, juices, and beverages
5. **Packaged Foods** - Packaged and canned foods
6. **Personal Care** - Hygiene and personal care products
7. **Health & Wellness** - Health supplements and wellness products
8. **Household Essentials** - Cleaning and household items

## How to Use

### Accessing the Vendor Panel

1. **Login/Register**: Create an account or login to your existing account
2. **Go to Vendor Panel**: Click on "Account" in the header dropdown menu, then select "📦 Vendor Panel"
3. **View Dashboard**: You'll see all your products listed in a table format

### Adding a Product

1. Click the **"Add New Product"** button on the dashboard
2. Fill in the product details:
   - **Product Name**: Enter the name of your product
   - **Category**: Select the appropriate category from the dropdown
   - **Description**: Provide a detailed description of the product
   - **Price (₹)**: Enter the price of the product
   - **Quantity**: Enter the quantity in stock
   - **Image**: Upload a product image (optional)
   - **Active Product**: Check the box to make the product active
3. Click **"Add Product"** to save

### Editing a Product

1. On the dashboard, click the **"Edit"** button next to the product you want to update
2. Modify the product details as needed
3. Click **"Update Product"** to save changes

### Deleting a Product

1. On the dashboard, click the **"Delete"** button next to the product
2. Confirm the deletion when prompted
3. The product will be removed from your listing

## Database Models

### Category Model

- `name` (CharField): Category name
- `description` (TextField): Category description
- `created_at` (DateTimeField): Creation timestamp

### Product Model

- `vendor` (ForeignKey): Reference to the User who added the product
- `category` (ForeignKey): Reference to the product category
- `name` (CharField): Product name
- `description` (TextField): Product description
- `price` (DecimalField): Product price
- `quantity` (IntegerField): Stock quantity
- `image` (ImageField): Product image
- `is_active` (BooleanField): Product status
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

## URLs

- `/vendor/` - Vendor dashboard
- `/vendor/add-product/` - Add new product
- `/vendor/edit-product/<product_id>/` - Edit product
- `/vendor/delete-product/<product_id>/` - Delete product

## Setup Instructions

### Prerequisites

- Python 3.8+
- Django 5.2+
- Pillow (for image handling)

### Installation

1. Add 'vendor' to INSTALLED_APPS in settings.py ✓ (Already done)
2. Create and apply migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Add sample categories:
   ```
   python manage.py add_categories
   ```

### Admin Panel

Access `/admin/` to manage products and categories through the Django admin interface.

## Security Features

- **Authentication Required**: Only logged-in users can access vendor functions
- **Vendor-Specific Access**: Vendors can only edit/delete their own products
- **CSRF Protection**: All forms are protected against CSRF attacks
- **User Validation**: Products are linked to the authenticated user

## Troubleshooting

### Missing Product Categories

If categories are not showing up, run:

```
python manage.py add_categories
```

### Media Files Not Loading

Ensure `MEDIA_URL` and `MEDIA_ROOT` are configured in settings.py and media directory has proper permissions.

### Permission Denied Error

Make sure you're logged in and trying to access/edit your own products only.

## Future Enhancements

- Product search and filtering
- Bulk upload of products
- Product reviews and ratings
- Order management for vendors
- Inventory tracking and alerts
- Analytics and sales reports

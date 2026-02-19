# Quick Commerce Django – API Documentation

## Overview

This project is primarily a **server-rendered Django web app**.
Most endpoints return HTML pages (not JSON), with one JSON endpoint for pincode availability.

- Base app routes: `/`
- Vendor routes: `/vendor/`
- Admin: `/admin/`

---

## Authentication & Session

- Uses Django session authentication.
- CSRF protection applies to all POST forms.
- Endpoints marked **Login required** need an authenticated user.
- Vendor dashboard/product/order/report endpoints require approved vendor access.

---

## User Routes (`/`)

### Public Pages

| Method | Path                         | Description                                       | Auth |
| ------ | ---------------------------- | ------------------------------------------------- | ---- |
| GET    | `/`                          | Home page with products and categories            | No   |
| GET    | `/category/<category_slug>/` | Product listing by category                       | No   |
| GET    | `/contact/`                  | Contact form page                                 | No   |
| POST   | `/contact/`                  | Submit contact form + sends acknowledgement email | No   |

### User Auth

| Method | Path         | Description                    | Auth |
| ------ | ------------ | ------------------------------ | ---- |
| GET    | `/login/`    | Login page                     | No   |
| POST   | `/login/`    | Login with username/password   | No   |
| GET    | `/register/` | Registration page              | No   |
| POST   | `/register/` | Create account + welcome email | No   |
| GET    | `/logout/`   | Logout user                    | Yes  |

### Delivery Pincode

| Method | Path                             | Description                           | Auth |
| ------ | -------------------------------- | ------------------------------------- | ---- |
| POST   | `/set-delivery-pincode/`         | Save pincode in session               | No   |
| GET    | `/check-pincode/?pincode=XXXXXX` | Check availability for pincode (JSON) | No   |

#### JSON response: `GET /check-pincode/`

```json
{
  "available": true,
  "pincode": "560001",
  "message": "Delivery available for 560001"
}
```

### Orders, Cart, Checkout

| Method | Path                               | Description                                  | Auth |
| ------ | ---------------------------------- | -------------------------------------------- | ---- |
| GET    | `/track-orders/`                   | User order history                           | Yes  |
| GET    | `/cart/`                           | View cart                                    | Yes  |
| GET    | `/add-to-cart/<product_slug>/`     | Add/increment product in cart                | Yes  |
| GET    | `/update-cart/<item_id>/<action>/` | Update cart item (`increment` / `decrement`) | Yes  |
| GET    | `/remove-from-cart/<item_id>/`     | Remove cart item                             | Yes  |
| GET    | `/checkout/`                       | Checkout page                                | Yes  |
| POST   | `/process-checkout/`               | Create order from cart data                  | Yes  |

#### `POST /process-checkout/` form fields

- `name` (required)
- `phone` (required)
- `address` (required, must contain 6-digit pincode)
- `payment_method` (required; e.g. `cod`, `online`, `upi`, `card`)

---

## Vendor Routes (`/vendor/`)

### Vendor Auth

| Method | Path                        | Description                            | Auth |
| ------ | --------------------------- | -------------------------------------- | ---- |
| GET    | `/vendor/signup/`           | Vendor signup page                     | No   |
| POST   | `/vendor/signup/`           | Register vendor + pending status email | No   |
| GET    | `/vendor/login/`            | Vendor login page                      | No   |
| POST   | `/vendor/login/`            | Vendor login with status checks        | No   |
| GET    | `/vendor/logout/`           | Vendor logout                          | Yes  |
| GET    | `/vendor/pending-approval/` | Pending approval page                  | Yes  |

### Vendor Dashboard & Profile

| Method | Path                 | Description              | Auth            |
| ------ | -------------------- | ------------------------ | --------------- |
| GET    | `/vendor/dashboard/` | Vendor metrics dashboard | Approved Vendor |
| GET    | `/vendor/profile/`   | Vendor profile page      | Approved Vendor |
| POST   | `/vendor/profile/`   | Update vendor profile    | Approved Vendor |
| GET    | `/vendor/contact/`   | Vendor contact page      | Yes             |
| POST   | `/vendor/contact/`   | Vendor contact submit    | Yes             |

### Product Management

| Method | Path                                      | Description                      | Auth            |
| ------ | ----------------------------------------- | -------------------------------- | --------------- |
| GET    | `/vendor/products/`                       | Product list (filters supported) | Approved Vendor |
| GET    | `/vendor/products/add/`                   | Add product page                 | Approved Vendor |
| POST   | `/vendor/products/add/`                   | Create product                   | Approved Vendor |
| GET    | `/vendor/products/<product_slug>/edit/`   | Edit product page                | Approved Vendor |
| POST   | `/vendor/products/<product_slug>/edit/`   | Update product                   | Approved Vendor |
| GET    | `/vendor/products/<product_slug>/delete/` | Delete confirmation page         | Approved Vendor |
| POST   | `/vendor/products/<product_slug>/delete/` | Delete product                   | Approved Vendor |
| GET    | `/vendor/products/<product_slug>/toggle/` | Toggle available/unavailable     | Approved Vendor |

#### Product list query params

- `category=<category_slug>`
- `availability=available|unavailable`

### Order Management

| Method | Path                                            | Description                                 | Auth            |
| ------ | ----------------------------------------------- | ------------------------------------------- | --------------- |
| GET    | `/vendor/orders/`                               | Vendor order items list (filters supported) | Approved Vendor |
| GET    | `/vendor/orders/<order_item_id>/`               | Order item detail                           | Approved Vendor |
| GET    | `/vendor/orders/<order_item_id>/update-status/` | Status update form                          | Approved Vendor |
| POST   | `/vendor/orders/<order_item_id>/update-status/` | Update status + sends customer email        | Approved Vendor |

#### Vendor orders query params

- `status=<status>`
- `date_from=YYYY-MM-DD`
- `date_to=YYYY-MM-DD`

### Earnings & Reports

| Method | Path                           | Description                     | Auth            |
| ------ | ------------------------------ | ------------------------------- | --------------- |
| GET    | `/vendor/earnings/`            | Earnings dashboard with filters | Approved Vendor |
| GET    | `/vendor/earnings/export-csv/` | Export delivered sales CSV      | Approved Vendor |

#### Earnings query params

- `date_from=YYYY-MM-DD`
- `date_to=YYYY-MM-DD`
- `product=<product_slug>`
- `category=<category_slug>`

---

## Response Types Summary

- HTML views: most endpoints
- JSON: `/check-pincode/`
- File download (CSV): `/vendor/earnings/export-csv/`

---

## Notes

- There is no DRF/OpenAPI schema yet.
- If needed, you can add Django REST Framework + Swagger (drf-yasg or drf-spectacular) as a next step.

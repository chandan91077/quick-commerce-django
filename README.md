# Quick Commerce Django

A quick-commerce web application built with Django.

This project includes:

- Customer storefront (browse categories, product detail page, cart, checkout)
- Delivery pincode availability check
- Vendor onboarding and vendor dashboard
- Vendor product, order, and earnings management

---

## Tech Stack (and what each is used for)

- **Python 3.11**: Core programming language
- **Django 5.2**: Web framework (routing, models, templates, auth, admin)
- **MySQL** (`mysqlclient`): Primary relational database for app data
- **SQLite**: Local fallback DB file exists (`db.sqlite3`) for simple development scenarios
- **Pillow**: Image upload/processing support for product and vendor media
- **Bootstrap + HTML/CSS + JS**: Frontend styling and interactions in server-rendered templates
- **GitHub Actions**: CI pipeline for migrations, checks, and tests

---

## Main Features

### Customer Side

- Home page with categories and product cards
- Category-wise product listing
- Product details page via slug URL (`/product/<slug>/`)
- User registration/login/logout
- Cart management and checkout
- Order tracking page
- Delivery pincode save/check endpoint

### Vendor Side

- Vendor signup/login with approval status flow
- Vendor dashboard and profile update
- Product CRUD (add/edit/delete/toggle availability)
- Order status management
- Earnings report and CSV export

---

## Project Structure

- `finalproject/` - Django project settings and root URLs
- `user/` - customer-facing views, models, URLs
- `vendor/` - vendor-facing views, models, URLs
- `templates/` - Django templates
- `static/` - CSS, JS, and static images
- `media/` - uploaded product/vendor files
- `.github/workflows/` - CI workflows

---

## Prerequisites

- Python `3.11+`
- MySQL Server `8+`
- Git

---

## Local Setup

### 1) Clone and open project

```bash
git clone <your-repo-url>
cd quick-commerce-django
```

### 2) Create and activate virtual environment

#### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Configure environment variables

Create `.env` in project root (`quick-commerce-django/.env`):

```env
SECRET_KEY=your_django_secret_key

DB_NAME=Finalprojects
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_app_password
DEFAULT_FROM_EMAIL=Blinkit <your_email@example.com>
```

> The project reads these values in `finalproject/settings.py`.

### 5) Create database in MySQL

```sql
CREATE DATABASE Finalprojects;
```

### 6) Apply migrations

```bash
python manage.py migrate
```

### 7) (Optional) Seed categories

```bash
python create_categories.py
```

### 8) Run server

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

---

## Docker Setup (Alternative)

### Quick Start with Docker Compose

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd quick-commerce-django
   ```

2. **Configure environment variables**

   Copy the Docker environment template:

   ```bash
   cp .env.docker .env
   ```

   Update `.env` with your actual values (especially `SECRET_KEY`, email credentials).

3. **Build and run containers**

   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Django app: `http://localhost:8000`
   - MySQL: `localhost:3306`

5. **Run management commands**

   ```bash
   # Create superuser
   docker-compose exec web python manage.py createsuperuser

   # Seed categories
   docker-compose exec web python create_categories.py

   # Run migrations
   docker-compose exec web python manage.py migrate
   ```

6. **Stop containers**
   ```bash
   docker-compose down
   ```

### Build Docker Image Only

To build just the Django app image:

```bash
docker build -t quickcommerce-django .
```

To run the image (requires external MySQL):

```bash
docker run -p 8000:8000 --env-file .env quickcommerce-django
```

---

## Useful Commands

```bash
python manage.py check
python manage.py test
python manage.py createsuperuser
python manage.py makemigrations
python manage.py migrate
```

---

## API/Route Notes

- Most routes render HTML templates (server-rendered pages).
- JSON endpoint: `GET /check-pincode/?pincode=XXXXXX`
- Full route reference: see `API_DOCUMENTATION.md`

---

## CI Workflow

GitHub Actions workflow is available at:

- `.github/workflows/django-ci.yml`

It runs on push and pull requests, and performs:

- dependency installation
- migrations
- `manage.py check`
- tests

---

## Security Notes

- Do **not** commit real credentials in code or `.env`.
- Rotate any exposed secrets (DB password, email app password) before production.
- Set `DEBUG=False` and strict `ALLOWED_HOSTS` in production.

---

## Known Development Tips

- If port 8000 is busy, run:
  ```bash
  python manage.py runserver 8001
  ```
- If MySQL connection fails, verify:
  - MySQL service is running
  - `.env` values are correct
  - database exists

---

## Documentation

- Vendor-specific guide: `VENDOR_README.md`
- API and endpoint summary: `API_DOCUMENTATION.md`

---

## License

added new line

This project is for learning/internal use unless you add a license file.

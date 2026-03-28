# Hotel Management Backend (DRF APIs Only)

Simple Django REST Framework backend for:
- orders + receipts
- payments
- daily reports

## Tech
- Django 5
- Django REST Framework
- SQLite (default)

## Run Locally
```bash
cd "/home/hamza/Desktop/Hotel Management System"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Base
`/api/v1/`

## Endpoints
- `GET/POST /api/v1/menu-items/`
- `GET/POST /api/v1/orders/`
- `GET/PATCH /api/v1/orders/{id}/`
- `POST /api/v1/orders/{id}/add-item/`
- `POST /api/v1/orders/{id}/close/`
- `GET /api/v1/receipts/{id}/`
- `POST /api/v1/payments/`
- `GET /api/v1/reports/daily-sales/?date=YYYY-MM-DD`
- `GET /api/v1/reports/payment-summary/?date=YYYY-MM-DD`

## Deploy (Vercel + Neon Postgres)

1) Create a Postgres database (Neon)
- Go to neon.tech, create a project, copy the connection string (use the “psycopg3”/“Django” style).
- Example `DATABASE_URL`:
  ```
  postgresql://USER:PASSWORD@HOST/dbname?sslmode=require
  ```

2) Add production settings
- We ship `config/settings_prod.py` that reads `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`, and uses WhiteNoise.

3) Configure Vercel
- Add these env vars in Vercel Project Settings → Environment Variables:
  - `DJANGO_SETTINGS_MODULE = config.settings_prod`
  - `SECRET_KEY = <generate a long random string>`
  - `DATABASE_URL = <your Neon URL with sslmode=require>`
  - `ALLOWED_HOSTS = <your-vercel-domain>.vercel.app`
  - `VERCEL_URL = <your-vercel-domain>.vercel.app`

4) First deploy
- Push the repo to GitHub (already done) and import in Vercel.
- Access docs at `/api/docs/`.

5) Run DB migrations in production
- Use a one-off run locally pointing to Neon:
  ```bash
  # Locally:
  export DATABASE_URL=postgresql://USER:PASSWORD@HOST/db?sslmode=require
  export DJANGO_SETTINGS_MODULE=config.settings_prod
  python manage.py migrate
  ```
  (Alternatively, use a Vercel build script or a GitHub Action to run `migrate` against Neon.)

Notes:
- SQLite is only for local dev. For production use the Postgres `DATABASE_URL`.
- Static files for the admin are served by WhiteNoise; for a pure API, this is sufficient.

## Sample Flow
1) Create menu item:
```json
POST /api/v1/menu-items/
{
  "name": "Burger",
  "price": "25.00",
  "is_active": true
}
```

2) Create order:
```json
POST /api/v1/orders/
{
  "customer_name": "Hamza"
}
```

3) Add item to order:
```json
POST /api/v1/orders/{order_id}/add-item/
{
  "menu_item_id": 1,
  "qty": 2
}
```

4) Close order and generate receipt:
```json
POST /api/v1/orders/{order_id}/close/
{
  "tax_percent": "10.00"
}
```

5) Add payment:
```json
POST /api/v1/payments/
{
  "receipt": 1,
  "method": "cash",
  "amount": "55.00",
  "reference": ""
}
```

## Rules Applied
- item price is snapshotted in `OrderItem.unit_price_snapshot`
- receipt is generated when order is closed
- payments cannot exceed receipt total

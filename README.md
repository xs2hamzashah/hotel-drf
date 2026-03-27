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
pip install django djangorestframework
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

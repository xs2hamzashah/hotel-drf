from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import MenuItem, Order, Payment, Receipt


class OrderFlowAPITest(APITestCase):
    def test_create_order_add_item_and_close_generates_receipt(self):
        menu_item = MenuItem.objects.create(name="Burger", price=Decimal("25.00"), is_active=True)
        order_response = self.client.post("/api/v1/orders/", {"customer_name": "Ali"}, format="json")
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        order_id = order_response.data["id"]

        add_item_response = self.client.post(
            f"/api/v1/orders/{order_id}/add-item/",
            {"menu_item_id": menu_item.id, "qty": 2},
            format="json",
        )
        self.assertEqual(add_item_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(add_item_response.data["line_total"]), "50.00")

        close_response = self.client.post(
            f"/api/v1/orders/{order_id}/close/",
            {"tax_percent": "10.00"},
            format="json",
        )
        self.assertEqual(close_response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(close_response.data["subtotal"]), "50.00")
        self.assertEqual(str(close_response.data["tax_amount"]), "5.00")
        self.assertEqual(str(close_response.data["total"]), "55.00")

    def test_payment_cannot_exceed_receipt_total(self):
        order = Order.objects.create(customer_name="Sara")
        receipt = Receipt.objects.create(
            order=order,
            subtotal=Decimal("100.00"),
            tax_percent=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total=Decimal("100.00"),
        )

        first_payment = self.client.post(
            "/api/v1/payments/",
            {"receipt": receipt.id, "method": "cash", "amount": "70.00"},
            format="json",
        )
        self.assertEqual(first_payment.status_code, status.HTTP_201_CREATED)

        second_payment = self.client.post(
            "/api/v1/payments/",
            {"receipt": receipt.id, "method": "card", "amount": "40.00"},
            format="json",
        )
        self.assertEqual(second_payment.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Payment exceeds receipt total.", str(second_payment.data))


class ReportsAPITest(APITestCase):
    def test_daily_sales_and_payment_summary_reports(self):
        order = Order.objects.create(customer_name="Kareem")
        receipt = Receipt.objects.create(
            order=order,
            subtotal=Decimal("80.00"),
            tax_percent=Decimal("5.00"),
            tax_amount=Decimal("4.00"),
            total=Decimal("84.00"),
        )
        Payment.objects.create(receipt=receipt, method="cash", amount=Decimal("20.00"))
        Payment.objects.create(receipt=receipt, method="card", amount=Decimal("64.00"))

        report_date = timezone.localdate().isoformat()
        daily_response = self.client.get(f"/api/v1/reports/daily-sales/?date={report_date}")
        self.assertEqual(daily_response.status_code, status.HTTP_200_OK)
        self.assertEqual(daily_response.data["receipts_count"], 1)
        self.assertEqual(str(daily_response.data["total_sales"]), "84")

        payment_response = self.client.get(f"/api/v1/reports/payment-summary/?date={report_date}")
        self.assertEqual(payment_response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(payment_response.data["total_collected"]), "84")
        self.assertEqual(len(payment_response.data["by_method"]), 2)

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from .models import Order, Receipt


def calculate_order_subtotal(order: Order) -> Decimal:
    subtotal = order.items.aggregate(total=Sum("line_total"))["total"]
    return subtotal or Decimal("0.00")


@transaction.atomic
def close_order_and_generate_receipt(order: Order, tax_percent: Decimal = Decimal("0.00")) -> Receipt:
    if order.status == Order.Status.CLOSED and hasattr(order, "receipt"):
        return order.receipt
    if order.status == Order.Status.CANCELLED:
        raise ValueError("Cancelled order cannot be closed.")

    subtotal = calculate_order_subtotal(order)
    if subtotal <= 0:
        raise ValueError("Cannot close an order without items.")

    tax_amount = (subtotal * tax_percent) / Decimal("100.00")
    total = subtotal + tax_amount

    order.status = Order.Status.CLOSED
    order.save(update_fields=["status", "updated_at"])

    receipt = Receipt.objects.create(
        order=order,
        subtotal=subtotal,
        tax_percent=tax_percent,
        tax_amount=tax_amount,
        total=total,
    )
    return receipt

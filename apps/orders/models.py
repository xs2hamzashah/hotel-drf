from django.db import models
from django.utils import timezone


class MenuItem(models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PREPARING = "preparing", "Preparing"
        SERVED = "served", "Served"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    order_no = models.CharField(max_length=24, unique=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    customer_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_no

    @staticmethod
    def next_order_no():
        today = timezone.localdate().strftime("%Y%m%d")
        prefix = f"ORD-{today}-"
        last = Order.objects.filter(order_no__startswith=prefix).order_by("order_no").last()
        if not last:
            return f"{prefix}0001"
        sequence = int(last.order_no.split("-")[-1]) + 1
        return f"{prefix}{sequence:04d}"

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = self.next_order_no()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name="order_items")
    qty = models.PositiveIntegerField()
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_no} - {self.menu_item.name}"


class Receipt(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="receipt")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RCP-{self.id}"


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        TRANSFER = "transfer", "Transfer"

    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=16, choices=Method.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"PAY-{self.id}"

from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from .models import Category, MenuItem, Order, OrderItem, Payment, Receipt


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "name",
            "price",
            "is_active",
            "category",
            "category_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "category_name"]


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    menu_item_category_id = serializers.IntegerField(source="menu_item.category_id", read_only=True)
    menu_item_category_name = serializers.CharField(source="menu_item.category.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_item_name",
            "menu_item_category_id",
            "menu_item_category_name",
            "qty",
            "unit_price_snapshot",
            "line_total",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "unit_price_snapshot",
            "line_total",
            "created_at",
            "menu_item_name",
            "menu_item_category_id",
            "menu_item_category_name",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_no",
            "status",
            "customer_name",
            "created_at",
            "updated_at",
            "subtotal",
            "items",
        ]
        read_only_fields = ["id", "order_no", "created_at", "updated_at", "subtotal", "items"]

    def get_subtotal(self, obj):
        subtotal = obj.items.aggregate(total=Sum("line_total"))["total"]
        return subtotal or Decimal("0.00")


class AddOrderItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)

    def validate_menu_item_id(self, value):
        if not MenuItem.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Active menu item not found.")
        return value


class ReceiptSerializer(serializers.ModelSerializer):
    order_no = serializers.CharField(source="order.order_no", read_only=True)

    class Meta:
        model = Receipt
        fields = [
            "id",
            "order",
            "order_no",
            "subtotal",
            "tax_percent",
            "tax_amount",
            "total",
            "issued_at",
        ]
        read_only_fields = fields


class CloseOrderSerializer(serializers.Serializer):
    tax_percent = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=Decimal("0.00"))


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "receipt", "method", "amount", "paid_at", "reference"]
        read_only_fields = ["id", "paid_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        return value

    def validate(self, attrs):
        receipt = attrs["receipt"]
        amount = attrs["amount"]
        paid_total = receipt.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        if paid_total + amount > receipt.total:
            raise serializers.ValidationError("Payment exceeds receipt total.")
        return attrs

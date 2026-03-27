from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MenuItem, Order, OrderItem, Payment, Receipt
from .serializers import (
    AddOrderItemSerializer,
    CloseOrderSerializer,
    MenuItemSerializer,
    OrderSerializer,
    PaymentSerializer,
    ReceiptSerializer,
)
from .services import close_order_and_generate_receipt


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by("-created_at")
    serializer_class = MenuItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related("items__menu_item").order_by("-created_at")
    serializer_class = OrderSerializer

    @action(detail=True, methods=["post"], url_path="add-item")
    def add_item(self, request, pk=None):
        order = self.get_object()
        serializer = AddOrderItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menu_item = MenuItem.objects.get(id=serializer.validated_data["menu_item_id"], is_active=True)
        qty = serializer.validated_data["qty"]
        unit_price = menu_item.price
        line_total = unit_price * qty

        if order.status in [Order.Status.CLOSED, Order.Status.CANCELLED]:
            return Response({"detail": "Cannot add items to closed/cancelled order."}, status=status.HTTP_400_BAD_REQUEST)

        order_item = OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            qty=qty,
            unit_price_snapshot=unit_price,
            line_total=line_total,
        )
        return Response(
            {
                "id": order_item.id,
                "order": order.id,
                "menu_item": menu_item.id,
                "qty": order_item.qty,
                "unit_price_snapshot": order_item.unit_price_snapshot,
                "line_total": order_item.line_total,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        order = self.get_object()
        serializer = CloseOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tax_percent = serializer.validated_data["tax_percent"]

        try:
            receipt = close_order_and_generate_receipt(order, tax_percent=tax_percent)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ReceiptSerializer(receipt).data, status=status.HTTP_200_OK)


class ReceiptViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Receipt.objects.select_related("order").all()
    serializer_class = ReceiptSerializer


class PaymentViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Payment.objects.select_related("receipt").all()
    serializer_class = PaymentSerializer

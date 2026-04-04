from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Category, MenuItem, Order, OrderItem, Payment, Receipt
from .filters import CategoryFilter, MenuItemFilter, OrderFilter
from .serializers import (
    CategorySerializer,
    AddOrderItemSerializer,
    CloseOrderSerializer,
    OrderItemSerializer,
    MenuItemSerializer,
    OrderSerializer,
    PaymentSerializer,
    ReceiptSerializer,
)
from .services import close_order_and_generate_receipt


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related("category").all().order_by("-created_at")
    serializer_class = MenuItemSerializer
    filterset_class = MenuItemFilter


class OrderViewSet(viewsets.ModelViewSet):
    queryset = (
        Order.objects.all()
        .prefetch_related("items__menu_item__category")
        .order_by("-created_at")
    )
    serializer_class = OrderSerializer
    filterset_class = OrderFilter

    @extend_schema(
        request=AddOrderItemSerializer,
        responses={201: OrderItemSerializer},
        summary="Add an item to the order",
        description="Adds a `menu_item` with given `qty` to this order. Not allowed when order is closed or cancelled.",
    )
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
        return Response(OrderItemSerializer(order_item).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=CloseOrderSerializer,
        responses={200: ReceiptSerializer},
        summary="Close order and generate receipt",
        description="Closes the order and generates a receipt using the provided `tax_percent`.",
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

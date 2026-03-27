from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MenuItemViewSet, OrderViewSet, PaymentViewSet, ReceiptViewSet

router = DefaultRouter()
router.register(r"menu-items", MenuItemViewSet, basename="menu-item")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"receipts", ReceiptViewSet, basename="receipt")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
]

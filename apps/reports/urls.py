from django.urls import path

from .views import DailySalesReportView, PaymentSummaryReportView

urlpatterns = [
    path("daily-sales/", DailySalesReportView.as_view(), name="daily-sales-report"),
    path("payment-summary/", PaymentSummaryReportView.as_view(), name="payment-summary-report"),
]

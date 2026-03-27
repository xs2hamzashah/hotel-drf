from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from django.utils.timezone import make_aware
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Payment, Receipt


def _resolve_day_bounds(date_str: str):
    parsed = datetime.strptime(date_str, "%Y-%m-%d")
    start = make_aware(datetime(parsed.year, parsed.month, parsed.day, 0, 0, 0))
    end = make_aware(datetime(parsed.year, parsed.month, parsed.day, 23, 59, 59))
    return start, end


class DailySalesReportView(APIView):
    def get(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"detail": "date query parameter is required (YYYY-MM-DD)."}, status=400)

        try:
            start, end = _resolve_day_bounds(date_str)
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        receipts = Receipt.objects.filter(issued_at__range=[start, end]).only("subtotal", "tax_amount", "total")
        subtotal = sum((receipt.subtotal for receipt in receipts), Decimal("0.00"))
        tax_amount = sum((receipt.tax_amount for receipt in receipts), Decimal("0.00"))
        total_sales = sum((receipt.total for receipt in receipts), Decimal("0.00"))
        data = {
            "date": date_str,
            "receipts_count": len(receipts),
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total_sales": total_sales,
        }
        return Response(data)


class PaymentSummaryReportView(APIView):
    def get(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"detail": "date query parameter is required (YYYY-MM-DD)."}, status=400)

        try:
            start, end = _resolve_day_bounds(date_str)
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        payments = list(Payment.objects.filter(paid_at__range=[start, end]).only("method", "amount"))
        by_method = defaultdict(lambda: Decimal("0.00"))
        for payment in payments:
            by_method[payment.method] += payment.amount

        rows = [{"method": method, "total": total} for method, total in sorted(by_method.items())]
        total = sum((payment.amount for payment in payments), Decimal("0.00"))
        return Response({"date": date_str, "total_collected": total, "by_method": rows})

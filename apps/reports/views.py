from datetime import datetime

from django.db.models import Sum
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

        receipts = Receipt.objects.filter(issued_at__range=[start, end])
        totals = receipts.aggregate(
            subtotal=Sum("subtotal"),
            tax_amount=Sum("tax_amount"),
            total_sales=Sum("total"),
        )
        data = {
            "date": date_str,
            "receipts_count": receipts.count(),
            "subtotal": totals["subtotal"] or 0,
            "tax_amount": totals["tax_amount"] or 0,
            "total_sales": totals["total_sales"] or 0,
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

        rows = (
            Payment.objects.filter(paid_at__range=[start, end])
            .values("method")
            .annotate(total=Sum("amount"))
            .order_by("method")
        )
        total = Payment.objects.filter(paid_at__range=[start, end]).aggregate(total=Sum("amount"))["total"] or 0
        return Response({"date": date_str, "total_collected": total, "by_method": list(rows)})

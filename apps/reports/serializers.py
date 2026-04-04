from rest_framework import serializers


class DailySalesReportSerializer(serializers.Serializer):
    date = serializers.CharField()
    receipts_count = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)


class PaymentSummaryRowSerializer(serializers.Serializer):
    method = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class PaymentSummaryReportSerializer(serializers.Serializer):
    date = serializers.CharField()
    total_collected = serializers.DecimalField(max_digits=12, decimal_places=2)
    by_method = PaymentSummaryRowSerializer(many=True)


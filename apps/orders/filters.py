import django_filters as filters

from .models import Category, MenuItem, Order


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    is_active = filters.BooleanFilter()

    class Meta:
        model = Category
        fields = ["name", "is_active"]


class MenuItemFilter(filters.FilterSet):
    category = filters.ModelChoiceFilter(queryset=Category.objects.all())
    category_id = filters.NumberFilter(field_name="category_id")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    is_active = filters.BooleanFilter()

    class Meta:
        model = MenuItem
        fields = ["category", "category_id", "name", "is_active"]


class OrderFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status")
    customer_name = filters.CharFilter(field_name="customer_name", lookup_expr="icontains")
    item_category = filters.ModelChoiceFilter(
        field_name="items__menu_item__category",
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Order
        fields = ["status", "customer_name", "item_category"]


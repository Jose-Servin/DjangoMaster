from typing import Any
from django.db import transaction
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = "Inventory"
    parameter_name = "inventory"  # this can be anything we want

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [("<10", "Low")]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    list_display = [
        "title",
        "unit_price",
        "inventory",
        "inventory_status",
        "collection_title",
    ]
    list_editable = ["unit_price"]
    list_per_page = 10
    list_select_related = ["collection"]
    list_filter = ["collection", "last_update", InventoryFilter]

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        """Displays inventory status based on the product's inventory level."""
        if product.inventory < 10:
            return "Low"
        return "Ok"

    def collection_title(self, product):
        """Returns the title of the collection to which the product belongs."""
        return product.collection.title

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        """Bulk action to reset the inventory of selected products to 10."""
        with transaction.atomic():
            updated_count = queryset.update(inventory=10)
            self.message_user(
                request,
                f"{updated_count} Products were successfully updated.",
                messages.SUCCESS
            )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders_count"]
    list_editable = ["membership"]
    list_per_page = 10
    ordering = ["first_name", "last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    def orders_count(self, customer):
        orders_changelist_url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html(
            f"<a href='{orders_changelist_url}'> {customer.orders_count} </a>"
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .annotate(
                # Customer has 'order_set' but we can shorthand to just 'order'
                orders_count=Count("order")
            )
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        product_changelist_url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html(
            f"<a href='{product_changelist_url}'> {
                collection.products_count} </a>"
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count("product"))


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]

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
    """
    Custom filter for the admin panel to filter products by inventory level.

    Attributes:
    - title (str): The label for the filter.
    - parameter_name (str): The name of the parameter used in the URL query string.

    Methods:
    - lookups(request, model_admin): Returns a list of filter options.
    - queryset(request, queryset): Filters the queryset based on the selected filter option.
    """

    title = "Inventory"
    parameter_name = "inventory"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        """
        Define the filter options.

        Returns:
        - A list of tuples where the first element is the filter value
            and the second element is the displayed name.
        """
        return [("<10", "Low")]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        """
        Filter the queryset based on the selected inventory filter.

        Returns:
        - A filtered queryset if the filter is applied, otherwise None.
        """
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Product model.

    Attributes:
    - autocomplete_fields (list): Fields with autocomplete functionality.
    - prepopulated_fields (dict): Fields that are automatically filled based on other fields.
    - actions (list): Custom actions available in the admin panel.
    - list_display (list): Fields to display in the list view.
    - list_editable (list): Fields that are editable directly in the list view.
    - list_filter (list): Filters available in the list view.
    - list_per_page (int): Number of items displayed per page.
    - list_select_related (list): Fields to optimize with select_related.
    - search_fields (list): Fields to search by in the admin panel.

    Methods:
    - collection_title(product): Returns the title of the collection to which the product belongs.
    - inventory_status(product): Displays the inventory status based on the product's inventory level.
    - clear_inventory(request, queryset): Bulk action to reset the inventory of selected products to 10.
    """

    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}
    actions = ["clear_inventory"]
    list_display = [
        "title",
        "unit_price",
        "inventory",
        "inventory_status",
        "collection_title",
    ]
    list_editable = ["unit_price"]
    list_filter = ["collection", "last_update", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]
    search_fields = ["title"]

    def collection_title(self, product):
        """Returns the title of the collection to which the product belongs."""
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        """
        Displays the inventory status based on the product's inventory level.

        Returns:
        - "Low" if the inventory is less than 10, otherwise "Ok".
        """
        if product.inventory < 10:
            return "Low"
        return "Ok"

    @admin.action(description="Clear Inventory")
    def clear_inventory(self, request, queryset):
        """
        Bulk action to reset the inventory of selected products to 10.

        Uses an atomic transaction to ensure that all updates are completed successfully.
        """
        with transaction.atomic():
            updated_count = queryset.update(inventory=10)
            self.message_user(
                request,
                f"{updated_count} Products were successfully updated.",
                messages.SUCCESS,
            )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Collection model.

    Attributes:
    - autocomplete_fields (list): Fields with autocomplete functionality.
    - list_display (list): Fields to display in the list view.
    - search_fields (list): Fields to search by in the admin panel.

    Methods:
    - products_count(collection): Returns the number of products in the collection
        as a clickable link to the filtered product list.
    - get_queryset(request): Annotates the queryset with the number of products in each collection.
    """

    autocomplete_fields = ["featured_product"]
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        """
        Returns the number of products in the collection as a clickable link to the filtered product list.

        The link redirects to the Product admin page, filtered by the selected collection.
        """
        product_changelist_url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html(
            f"<a href='{product_changelist_url}'>{collection.products_count}</a>"
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        """
        Annotates the queryset with the number of products in each collection.

        Returns:
        - The annotated queryset.
        """
        return super().get_queryset(request).annotate(products_count=Count("product"))


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Customer model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    - list_editable (list): Fields that are editable directly in the list view.
    - list_per_page (int): Number of items displayed per page.
    - list_select_related (list): Fields to optimize with select_related.
    - ordering (list): Default ordering of the list view.
    - search_fields (list): Fields to search by in the admin panel.

    Methods:
    - orders_count(customer): Returns the number of orders associated with the customer
        as a clickable link to the filtered order list.
    - get_queryset(request): Annotates the queryset with the number of orders for each customer.
    """

    list_display = ["first_name", "last_name", "membership", "orders_count"]
    list_editable = ["membership"]
    list_per_page = 10
    list_select_related = ["user"]
    ordering = ["user__first_name", "user__last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    def orders_count(self, customer):
        """
        Returns the number of orders associated with the customer as a clickable link to the filtered order list.

        The link redirects to the Order admin page, filtered by the selected customer.
        """
        orders_changelist_url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html(
            f"<a href='{orders_changelist_url}'>{customer.orders_count}</a>"
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        """
        Annotates the queryset with the number of orders for each customer.

        Returns:
        - The annotated queryset.
        """
        return super().get_queryset(request).annotate(orders_count=Count("order"))


class OrderItemInline(admin.TabularInline):
    """
    Inline admin class for OrderItem model to be displayed within the Order admin page.

    Attributes:
    - autocomplete_fields (list): Fields with autocomplete functionality.
    - model (model class): The model class this inline is for.
    - min_num (int): Minimum number of items required.
    - max_num (int): Maximum number of items allowed.
    """

    autocomplete_fields = ["product"]
    model = models.OrderItem
    min_num = 1
    max_num = 10


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Order model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    - autocomplete_fields (list): Fields with autocomplete functionality.
    - inlines (list): Inline models to display within the Order admin page.
    """

    list_display = ["id", "placed_at", "customer"]
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]

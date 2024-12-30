from os import read
from turtle import mode
from rest_framework import serializers
from django.db.models import Sum, F
from .models import (
    Cart,
    Customer,
    OrderItem,
    Product,
    Collection,
    Review,
    CartItem,
    Order,
)
from .signals import order_created
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction


class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Collection model.

    Adds a `product_count` field that returns the number of products in the collection.

    Attributes:
        product_count (SerializerMethodField): A field that calculates the number of products in the collection.
    """

    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ["id", "title", "product_count"]

    def get_product_count(self, collection: Collection):
        """
        Retrieves the product count for the collection.

        If the product count annotation is not present, returns 0.

        Args:
            collection (Collection): The collection instance.

        Returns:
            int: The number of products in the collection.
        """
        return getattr(collection, "product_count", 0)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    Adds a `price_w_tax` field that returns the price including tax.

    Attributes:
        price_w_tax (SerializerMethodField): A field that calculates the price with tax.
    """

    price_w_tax = serializers.SerializerMethodField(method_name="calculate_tax")

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "slug",
            "inventory",
            "unit_price",
            "price_w_tax",
            "collection",
        ]

    def calculate_tax(self, product: Product):
        """
        Calculates the price of the product including a 10% tax.

        Args:
            product (Product): The product instance.

        Returns:
            Decimal: The price with tax included.
        """
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.

    Overrides the `create` method to include the product ID from the context.

    Methods:
        create(validated_data): Creates a new review instance.
    """

    class Meta:
        model = Review
        fields = ["id", "date", "name", "description"]

    def create(self, validated_data):
        """
        Creates a new review instance with the associated product ID.

        Args:
            validated_data (dict): The validated data for the review.

        Returns:
            Review: The created review instance.
        """
        product_id = self.context["product_id"]
        return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for the Product model.

    This serializer is used for nested representations where only basic product information is needed.

    Fields:
        - id
        - title
        - unit_price
    """

    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the CartItem model.

    Includes a nested product representation and a total price field.

    Attributes:
        product (SimpleProductSerializer): Nested serializer for the product.
        total_price (SerializerMethodField): A field that calculates the total price for the cart item.
    """

    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cartItem: CartItem):
        """
        Calculates the total price for the cart item.

        Args:
            cartItem (CartItem): The cart item instance.

        Returns:
            Decimal: The total price for the cart item.
        """
        return cartItem.quantity * cartItem.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for adding an item to the cart.

    Includes validation for the product ID and custom save logic to handle
    creating or updating a cart item.

    Fields:
        - id
        - product_id
        - quantity
    """

    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        """
        Validates that the provided product ID exists.

        Args:
            value (int): The product ID.

        Raises:
            serializers.ValidationError: If no product with the given ID exists.

        Returns:
            int: The validated product ID.
        """
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product with the given ID exists.")
        return value

    def save(self, **kwargs):
        """
        Creates or updates a cart item with the provided data.

        If a cart item with the same product ID already exists, its quantity is updated.

        Returns:
            CartItem: The created or updated cart item instance.
        """
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]
        cart_id = self.context["cart_id"]

        try:
            # Update the quantity of an existing cart item
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # Create a new cart item
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for updating the quantity of a cart item.

    Fields:
        - quantity
    """

    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.

    Includes nested cart items and a total price field.

    Attributes:
        id (UUIDField): The unique identifier for the cart.
        items (CartItemSerializer): Nested serializer for the cart items.
        total_price (SerializerMethodField): A field that calculates the total price for the cart.
    """

    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        """
        Calculates the total price for all items in the cart.

        Args:
            cart (Cart): The cart instance.

        Returns:
            Decimal: The total price for all items in the cart, or 0 if the cart is empty.
        """
        total_price = cart.items.aggregate(
            total=Sum(F("quantity") * F("product__unit_price"))
        )["total"]
        return total_price or 0

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Customer model.

    Includes basic customer details and a reference to the associated user.

    Attributes:
        id (IntegerField): The unique identifier for the customer.
        user_id (PrimaryKeyRelatedField): The ID of the user associated with this customer.
        phone (CharField): The phone number of the customer.
        birth_date (DateField): The birth date of the customer.
        membership (CharField): The membership level of the customer (Bronze, Silver, Gold).
    """

    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "unit_price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "placed_at", "payment_status", "items"]


class CreateOrderSerializer(serializers.Serializer):

    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        """
        Validates that the provided cart ID exists.

        Args:
            value (UUID): The cart ID.

        Raises:
            serializers.ValidationError: If no cart with the given ID exists.

        Returns:
            UUID: The validated cart ID.
        """
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No cart with the given ID exists.")
        if CartItem.objects.filter(cart_id=value).count() == 0:
            raise serializers.ValidationError("The cart is empty.")
        return value

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            # print(f"Cart ID: {self.validated_data["cart_id"]}")
            # print(f"User ID: {self.context['user_id']}")

            # Get the Customer ID
            customer = Customer.objects.get(user_id=self.context["user_id"])
            order = Order.objects.create(customer=customer)

            # Get the cart items from this cart
            cart_items = CartItem.objects.select_related("product").filter(
                cart_id=cart_id
            )
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]

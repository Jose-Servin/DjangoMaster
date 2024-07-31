from rest_framework import serializers
from .models import Cart, Product, Collection, Review, CartItem
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ["id", "title", "product_count"]

    def get_product_count(self, collection: Collection):
        # If the annotation is not present, return None or 0
        return getattr(collection, "product_count", 0)


class ProductSerializer(serializers.ModelSerializer):
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

    price_w_tax = serializers.SerializerMethodField(
        method_name="calculate_tax")

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "date", "name", "description"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    # must follow the get_ naming convention
    def get_total_price(self, cartItem: CartItem):
        return cartItem.quantity * cartItem.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        cart_sum = 0

        for item in cart.items.all():
            item_sum = item.quantity * item.product.unit_price
            cart_sum += item_sum
        return cart_sum

    class Meta:
        model = Cart
        # Server returns these field to the Client
        # Client sends these fields to the Server
        fields = ["id", "items", "total_price"]

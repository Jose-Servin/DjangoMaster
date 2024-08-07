from rest_framework import serializers
from django.db.models import Sum, F
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

    price_w_tax = serializers.SerializerMethodField(method_name="calculate_tax")

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

    # must follow the get_<field-name> naming convention
    def get_total_price(self, cartItem: CartItem):
        return cartItem.quantity * cartItem.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product with the given ID exists.")
        return value

    def save(self, **kwargs):
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]
        cart_id = self.context["cart_id"]

        try:
            # a cart item exists so update the quantity
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # create a cart item because one does not exists
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    # we don't need to send this to the Server to create a Cart
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        total_price = cart.items.aggregate(
            total=Sum(F("quantity") * F("product__unit_price"))
        )["total"]
        return total_price or 0

    class Meta:
        model = Cart
        # Server returns these field to the Client
        # Client sends these fields to the Server
        fields = ["id", "items", "total_price"]

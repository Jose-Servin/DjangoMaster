from uuid import uuid4
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.contrib import admin

from store import permissions


class Promotion(models.Model):
    """
    Represents a promotional discount.

    Attributes:
        description (str): The description of the promotion.
        discount (float): The discount percentage applied by the promotion.
    """

    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    """
    Represents a collection of products.

    Attributes:
        title (str): The title of the collection.
        featured_product (ForeignKey): A reference to a featured product in the collection.
            - If the featured product is deleted, this field is set to null.
            - Related name is set to '+' to prevent reverse relation creation.
    """

    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, related_name="+", blank=True
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]


class Product(models.Model):
    """
    Represents a product available for purchase.

    Attributes:
        title (str): The name of the product.
        slug (SlugField): A short label for the product, used in URLs.
        description (str): A detailed description of the product.
        unit_price (Decimal): The price per unit of the product.
        inventory (int): The number of items available in stock.
        last_update (DateTime): The date and time when the product was last updated.
        collection (ForeignKey): A reference to the collection to which the product belongs.
            - Protects against deletion of the collection if products are still associated.
        promotions (ManyToManyField): A many-to-many relationship to promotions that apply to this product.
    """

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]


class Customer(models.Model):
    """
    Represents a customer who purchases products.

    Attributes:
        phone (str): The phone number of the customer.
        birth_date (Date): The birth date of the customer.
        membership (str): The membership level of the customer (Bronze, Silver, Gold).
        user (OneToOneField): A one-to-one relationship with the User model for authentication.

    Methods:
        first_name(): Returns the first name of the user associated with this customer.
        last_name(): Returns the last name of the user associated with this customer.
    """

    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @admin.display(ordering="user__first_name")
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self):
        return self.user.last_name

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        ordering = ["user__first_name", "user__last_name"]
        permissions = [("view_history", "Can view history")]


class Order(models.Model):
    """
    Represents an order placed by a customer.

    Attributes:
        placed_at (DateTime): The date and time when the order was placed.
        payment_status (str): The current payment status of the order (Pending, Complete, Failed).
        customer (ForeignKey): A reference to the customer who placed the order.
            - Protects against deletion of the customer if orders are still associated.
    """

    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETE = "C"
    PAYMENT_STATUS_FAILED = "F"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETE, "Complete"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [("cancel_order", "Can cancel Order")]


class OrderItem(models.Model):
    """
    Represents an item within an order.

    Attributes:
        order (ForeignKey): A reference to the order to which this item belongs.
            - Protects against deletion of the order if items are still associated.
        product (ForeignKey): A reference to the product being ordered.
            - Protects against deletion of the product if it is associated with an order item.
        quantity (int): The quantity of the product ordered.
        unit_price (Decimal): The price of the product at the time of the order.
    """

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orderitems"
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    """
    Represents a customer's address.

    Attributes:
        street (str): The street address.
        city (str): The city of the address.
        customer (ForeignKey): A reference to the customer who owns the address.
            - Deleting the customer will also delete their associated addresses.
    """

    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    """
    Represents a shopping cart.

    Attributes:
        id (UUIDField): The unique identifier for the cart, generated automatically.
        created_at (DateTime): The date and time when the cart was created.
    """

    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    """
    Represents an item within a shopping cart.

    Attributes:
        cart (ForeignKey): A reference to the cart to which this item belongs.
            - Deleting the cart will also delete its associated items.
        product (ForeignKey): A reference to the product being added to the cart.
            - Deleting the product will also delete its associated cart items.
        quantity (int): The quantity of the product added to the cart.

    Meta:
        unique_together: Ensures that each cart can only have one instance of a specific product.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [["cart", "product"]]


class Review(models.Model):
    """
    Represents a review of a product.

    Attributes:
        product (ForeignKey): A reference to the product being reviewed.
            - Deleting the product will also delete its associated reviews.
        name (str): The name of the reviewer.
        description (str): The content of the review.
        date (Date): The date the review was submitted.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

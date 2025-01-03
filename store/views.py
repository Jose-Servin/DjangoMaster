from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .permissions import (
    IsAdminOrReadOnly,
    FullDjangoModelPermissions,
    ViewCustomerHistoryPermission,
)
from .models import (
    Cart,
    CartItem,
    Customer,
    OrderItem,
    Product,
    Collection,
    Review,
    Order,
)
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CollectionSerializer,
    CustomerSerializer,
    ProductSerializer,
    ReviewSerializer,
    SimpleProductSerializer,
    UpdateCartItemSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    UpdateOrderSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    DjangoModelPermissions,
)
from rest_framework.pagination import PageNumberPagination
from .filters import ProductFilter
from .pagination import StandardResultsSetPagination


class ProductViewSet(ModelViewSet):
    """
    A viewset for viewing and editing product instances.

    Attributes:
        queryset: The base queryset for retrieving products.
        serializer_class: The serializer class used for validating and deserializing input, and for serializing output.
        filter_backends: A list of filter backends to apply to the viewset.
        filterset_class: The filterset class used for filtering the queryset.
        pagination_class: The pagination class used for paginating the results.
        search_fields: The fields to be searched in the search filter.
        ordering_fields: The fields that can be used to order the results.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = StandardResultsSetPagination
    search_fields = ["title", "description"]
    ordering_fields = ["unit_price", "last_update"]
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        """
        Adds extra context to the serializer.

        Returns:
            dict: The context dictionary to pass to the serializer.
        """
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a product instance.

        Prevents deletion if the product is associated with any order items.

        Returns:
            Response: An HTTP response object.
        """
        if OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted because it's associated with an Order Item."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    """
    A viewset for viewing and editing collection instances.

    Attributes:
        queryset: The base queryset for retrieving collections.
        serializer_class: The serializer class used for validating and deserializing input, and for serializing output.
    """

    queryset = Collection.objects.annotate(product_count=Count("product"))
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        """
        Adds extra context to the serializer.

        Returns:
            dict: The context dictionary to pass to the serializer.
        """
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a collection instance.

        Prevents deletion if the collection is associated with any products.

        Returns:
            Response: An HTTP response object.
        """
        collection_id = kwargs["pk"]
        if Product.objects.filter(collection_id=collection_id).exists():
            return Response(
                {
                    "error": "Collection cannot be deleted because it's associated with a Product."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    """
    A viewset for viewing and editing review instances.

    Attributes:
        serializer_class: The serializer class used for validating and deserializing input, and for serializing output.
    """

    serializer_class = ReviewSerializer

    def get_queryset(self):
        """
        Filters reviews by product.

        Returns:
            QuerySet: The filtered queryset of reviews.
        """
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        """
        Adds extra context to the serializer.

        Returns:
            dict: The context dictionary to pass to the serializer.
        """
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    """
    A viewset for viewing and editing cart instances.

    This viewset supports creation, retrieval, and deletion of carts.

    Attributes:
        queryset: The base queryset for retrieving carts.
        serializer_class: The serializer class used for validating and deserializing input, and for serializing output.
    """

    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    """
    A viewset for viewing and editing cart item instances.

    Supports only GET, POST, PATCH, and DELETE HTTP methods.

    Attributes:
        http_method_names: A list of allowed HTTP methods for the viewset.
    """

    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the HTTP method.

        Returns:
            Serializer: The serializer class.
        """
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        """
        Filters cart items by cart.

        Returns:
            QuerySet: The filtered queryset of cart items.
        """
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
            "product"
        )

    def get_serializer_context(self):
        """
        Adds extra context to the serializer.

        Returns:
            dict: The context dictionary to pass to the serializer.
        """
        return {"cart_id": self.kwargs["cart_pk"]}


class CustomerViewSet(ModelViewSet):
    """
    A viewset for viewing and editing customer instances.

    Supports GET, POST, PATCH, and DELETE HTTP methods.

    Attributes:
        queryset (QuerySet): The queryset of customer objects used for retrieving and editing.
        serializer_class (Serializer): The serializer class used for serializing and deserializing customer data.
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response("Ok")

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    """
    A viewset for viewing and editing order instances.

    Supports GET, POST, PATCH, and DELETE HTTP methods.

    Attributes:
        serializer_class (Serializer): The serializer class used for serializing and deserializing order data.
        permission_classes (list): The list of permission classes that determine access control.
    """

    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        """
        Returns the list of permissions that determine access control.

        Returns:
            list: The list of permission classes.
        """
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        create_serializer = CreateOrderSerializer(
            data=request.data, context={"user_id": self.request.user.id}
        )
        create_serializer.is_valid(raise_exception=True)
        order = create_serializer.save()
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id).order_by("placed_at")

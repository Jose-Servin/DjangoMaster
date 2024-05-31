from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Product, Collection
from .serializers import CollectionSerializer, ProductSerializer


@api_view(["GET", "POST"])
def product_list(request):
    if request.method == "GET":
        query_set = Product.objects.select_related("collection").all()
        serializer = ProductSerializer(
            query_set, many=True, context={"request": request}
        )
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def product_detail(request, id):
    product: Product = get_object_or_404(Product, pk=id)
    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == "PUT":
        # de-serialize incoming data and provide the product instance we are working on
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        """
        when we call the serializer.save() method,
        the serializer will call the update() method
        because we are instantiating it with a product instance
        """
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        if product.orderitems.count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted because it's associated with an Order Item."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def collection_list(request):
    if request.method == "GET":
        # `product_count` is only included in the response for `GET` requests
        query_set = Collection.objects.annotate(product_count=Count("product"))
        serializer = CollectionSerializer(
            query_set, many=True, context={"request": request}
        )
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(
        product_count=Count("product")), pk=pk)
    if request.method == "GET":
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == "PUT":
        # de-serialize incoming data and provide the collection instance we are working on
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        """
        when we call the serializer.save() method,
        the serializer will call the update() method
        because we are instantiating it with a collection instance
        """
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        if collection.product_set.count() > 0:
            return Response(
                {
                    "error": "Collection cannot be deleted because it's associated with a Product."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Product, Collection
from .serializers import CollectionSerializer, ProductSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        if product.orderitems.count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted because it's associated with an Order Item."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count("product"))
    serializer_class = CollectionSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def delete(self, request, *args, **kwargs):
        collection = self.get_object()
        if collection.product_set.count() > 0:
            return Response(
                {
                    "error": "Collection cannot be deleted because it's associated with a Product."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

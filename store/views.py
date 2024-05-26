from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer


@api_view()
def product_list(request):
    query_set = Product.objects.select_related("collection").all()
    serializer = ProductSerializer(query_set, many=True, context={"request": request})
    return Response(serializer.data)


@api_view()
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    serializer = ProductSerializer(product)

    return Response(serializer.data)


@api_view()
def collection_detail(response, pk):
    return Response("ok")

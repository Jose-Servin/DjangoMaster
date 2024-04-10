from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Customer, Collection, Order, OrderItem


def say_hello(request):
    #  query_set are lazy evaluated
    query_set = Product.objects.filter(
        Q(inventory__lt=10) | Q(unit_price__lt=20))
    res = {'name': 'Mosh', 'products': list(query_set)}
    return render(request, 'hello.html', res)

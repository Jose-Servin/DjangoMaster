from django.shortcuts import render
from django.db.models import Q, F
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Customer, Collection, Order, OrderItem


def say_hello(request):
    #  query_set are lazy evaluated
    query_set = Product.objects.values('id', 'title', 'collection__title')
    res = {'name': 'Mosh', 'products': list(query_set)}
    return render(request, 'hello.html', res)

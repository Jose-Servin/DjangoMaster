from django.shortcuts import render
from django.db.models import Q, F
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Customer, Collection, Order, OrderItem
from django.db.models import Count, Min, Sum, Value, Func
from django.db.models.functions import Concat


def say_hello(request):
    #  query_set are lazy evaluated

    query_set = Customer.objects.annotate(
        orders_placed=Count('order')
    )

    context = {'name': 'Mosh', 'query_set': list(query_set)}

    # Render the template with the context data
    return render(request, 'hello.html', context)

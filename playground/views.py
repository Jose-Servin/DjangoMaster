from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Customer, Collection, Order, OrderItem
from django.db.models import Count, Min, Sum, Value, Func, Q, F, ExpressionWrapper, DecimalField, Max
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType


def say_hello(request):
    #  query_set are lazy evaluated
    query_set = Customer.objects.annotate(
        last_order_id=Max('order__id')
    )

    context = {'name': 'Mosh', 'query_set': list(query_set)}

    # Render the template with the context data
    return render(request, 'hello.html', context)

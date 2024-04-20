from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Customer, Collection, Order, OrderItem
from django.db.models import Count, Min, Sum, Value, Func, Q, F, ExpressionWrapper, DecimalField, Max
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from tags.models import TaggedItem
from django.db import transaction


@transaction.atomic
def say_hello(request):
    #  query_set are lazy evaluated
    collection = Collection()
    collection.title = 'Video Games'
    collection.featured_product = Product(pk=1)
    collection.save()

    collection = Collection.objects.create(
        title='Video Games',
        featured_product_id=1
    )

    context = {'name': 'Mosh', 'query_set': list(query_set)}

    # Render the template with the context data
    return render(request, 'hello.html', context)

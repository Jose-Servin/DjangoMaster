# The Ultimate Django Series Part 1

## Django Fundamentals

What is this project about? "We will be using Django to build an API for an online store."

How to set up your Django Project:

1. Create your virtual environment and install all necessary packages.
2. Create your Django Project with `django-admin startproject {project-name} .`
3. Hide your `SECRET_KEY` from `storefront/settings.py`

### Creating your first App

In simplest terms, a Django project is a collection of apps that each provide a certain functionality.

This is done by running `django-admin startapp {app-name}`.

### Writing Views

In simplest terms, the `Views` directory for each application is a request handler. In here, we define what response should be returned to a user based on their request.

### Writing Models

1. Create Models
2. `python manage.py makemigrations`
3. `python manage.py migrate`
4. To see compiled sql we can use `python manage.py sqlmigrate {app} {migration sequence number}`

### Reverting Migrations

1. Find what migration you want to revert to and run `python manage.py migrate {app} {sequence-number}`
2. Remove all code changes and migration file associated with the migration you just deleted. Use `Git` here to help revert. For example, if you want to go back 1 commit, you can use `git reset --hard HEAD~1`

### Connecting MySQL to Django

1. [Download MySQL](https://dev.mysql.com/downloads/mysql/)
2. [Download DBeaver](https://dbeaver.io/download/)
3. Connect to MySQL using DBeaver and `root` user you created.
4. Execute `CREATE DATABASE storefront;` to create your database - pick whatever name you want.

5. Install the `mysqlclient` package (pip) and the `pkg-config` (brew)

   * See instructions [here](https://pypi.org/project/mysqlclient/)

6. In Django {project} {settings.py} switch the connection to MySQL - remember to NOT push your password.

    ```python
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "storefront",
            "HOST": "127.0.0.1",
            "PORT": "3306",
            "USER": "root",
            "PASSWORD": "BLANK"
        }
    }
    ```

7. Execute `python manage.py migrate` - any migrations you have will be applied to your MySQL Database.

* [YouTube Video - Connecting MySQL and Django](https://www.youtube.com/watch?v=SNyCV8vOr-g&ab_channel=StudyGyaan)

### Creating Empty Migrations

1. `python manage.py makemigrations store --empty`

This follows the format `python mange.py makemigrations {app} --empty`

```text
python manage.py makemigrations store --empty

Migrations for 'store':
  store/migrations/0005_auto_20240408_1705.py
```

Define your SQL migration

```python
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_auto_20240408_1703"),
    ]

    operations = [
        migrations.RunSQL(
            """ 
            INSERT INTO store_collection (title)
            VALUES ('collection1')
            """,
            """ 
            DELETE FROM store_collection
            WHERE title='collection1'
            """
        )
    ]
```

Execute your migration

```terminal
python manage.py migrate

Operations to perform:
  Apply all migrations: admin, auth, contenttypes, likes, sessions, store, tags
Running migrations:
  Applying store.0003_auto_20240408_1701... OK
  Applying store.0004_auto_20240408_1703... OK
  Applying store.0005_auto_20240408_1705... OK
```

To Undo the custom migration, we follow a similar process:

`python manage.py migrate {app} {sequence-number}`

Remember to refresh our database to view the changes AND delete the migration files from our {app}.

## Django ORM

### Managers and QuerySets

In Django, each `Model` we build has an `objects` attribute that opens up access to the database - which is called a `manager`. We can think of this `manager` as a remote control that gives us access to various database methods.

A `QuerySets` object is an object that encapsulates a database query and is lazy-evaluated. This means, no data is stored in memory but rather only presented if called.

This is done to allow for complex queries to be written which can reference previously defined query_sets.

```python
query_set = Product.objects.all()
```

### Retrieving Objects

`product = Product.objects.get(pk=1)`

* `pk` is translated to whatever the `primary key` field is for the specific model we are querying.

### Filtering Objects

For filtering, we will rely heavily on the [Field Lookup](https://docs.djangoproject.com/en/5.0/ref/models/querysets/#field-lookups) from Django's QuerySet API.

"Find all products that have a unit price greater than 20"

```python
query_set = Product.objects.filter(unit_price__gt=20)
```

We can also filter across relationships, we navigate the relationship by using the double underscore `__`; doing so now gives us access to all fields from our defined `Collection(models.Model)` class.

"Find all Products that are in Collection 1, 2 or 3".

```python
query_set = Product.objects.filter(collection__id__range=(1,2,3))
```

For `dates` we can use various field lookups and extract specific date parts.

"Find all products with a last update of 2021"

```python
query_set = Product.objects.filter(last_update__year=2021)
```

Null fields use the `__isnull` field lookup and evaluates to `True` or `False`.

```python
query_set = Product.objects.filter(decription__isnull=True)
```

### Complex Lookups using Q Objects

[Read the Docs](https://docs.djangoproject.com/en/5.0/topics/db/queries/#complex-lookups-with-q-objects)

Using Q objects to form an `or` SQL statement. "Find products that have inventory less than 10 OR unit price less than 20."

```python
query_set = Product.objects.filter(
        Q(inventory__lt=10) | Q(unit_price__lt=20))
```

We can see the compiled SQL in the Django Debug Toolbar.

```SQL
SELECT `store_product`.`id`,
       `store_product`.`title`,
       `store_product`.`slug`,
       `store_product`.`description`,
       `store_product`.`unit_price`,
       `store_product`.`inventory`,
       `store_product`.`last_update`,
       `store_product`.`collection_id`
  FROM `store_product`
 WHERE (`store_product`.`inventory` < 10 OR `store_product`.`unit_price` < 20)
```

Remember that with `filter()` we can only achieve `AND` condition checks. So this is checking for products with inventory less than 10 AND unit price less than 20.

```python
query_set = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
```

Q objects can also be used for `AND` conditions but they do become a bit verbose.

```python
query_set = Product.objects.filter(
        Q(inventory__lt=10) & Q(unit_price__lt=20))
```

Or we can negate conditions to say "Find products that have inventory less than 10 and their unit price is NOT less than 20."

```python
query_set = Product.objects.filter(
        Q(inventory__lt=10) & ~Q(unit_price__lt=20))
```

### Referencing Fields using F Objects

[Read the Docs](https://docs.djangoproject.com/en/5.0/ref/models/expressions/#f-expressions)

The scenario we are working on here is "find all products who's inventory = unit_price"

We can't directly reference `unit_price` since the expectation is that we provide a `key-value` pair.

```python
# not allowed
query_set = Product.objects.filter(inventory='unit_price')
```

So instead, we use and `F()` object

```python
query_set = Product.objects.filter(inventory=F('unit_price'))
```

In SQL this compiles to

```sql
SELECT `store_product`.`id`,
       `store_product`.`title`,
       `store_product`.`slug`,
       `store_product`.`description`,
       `store_product`.`unit_price`,
       `store_product`.`inventory`,
       `store_product`.`last_update`,
       `store_product`.`collection_id`
  FROM `store_product`
 WHERE `store_product`.`inventory` = (`store_product`.`unit_price`)
```

If we change the scenario to now be "Find all products who's inventory is equal to their collection id" using `F()` objects we write

```python
query_set = Product.objects.filter(inventory=F('collection__id'))
```

### Sorting Data

Sorting can be easily applied by the `order_by()` function. Remember that by default, the `ORDER BY {FIELD} ASC` is done in ascending order.

```python
query_set = Product.objects.order_by('title')
```

We can easily implement a `DESC` order by, by adding a negative `-`

```python
query_set = Product.objects.order_by('-title')
```

Or, we can use a combination of `order_by()` and `reverse()` methods to change the order by direction.

```python
# This orders by title in descending order 
query_set = Product.objects.order_by('title').reverse()
# achieves the same as 
query_set = Product.objects.order_by('-title')
```

Accessing first or last elements also come with 2 ways of implementation.

First way

```python
query_set = Product.objects.order_by('unit_price')[0]
```

Second way

```python
query_set = Product.objects.earliest('unit_price')
```

### Limiting Results

Often, we will be limiting the results we pass to our frontend by slicing our QuerySet into chunks/pages. This is done by using python array slicing syntax.

```python
query_set = Product.objects.all()[:5]
```

### Selecting Fields to Query

Up to this point, any `query_set` was returning ALL columns from the table we were querying. But now for this example, we are only interested in returning the `id` and `title` of our Products. We achieve this with the `.values()` method.

```python
query_set = Product.objects.values('id', 'title')
```

In SQL this compiles to

```SQL
SELECT `store_product`.`id`,
       `store_product`.`title`
  FROM `store_product`
```

We can also go one step further and bring in fields from different models such as `collection__title`

```python
query_set = Product.objects.values('id', 'title', 'collection__title')
```

This SQL now contains an `INNER JOIN` in order to bring in this new field.

```sql
SELECT `store_product`.`id`,
       `store_product`.`title`,
       `store_collection`.`title`
  FROM `store_product`
 INNER JOIN `store_collection`
    ON (`store_product`.`collection_id` = `store_collection`.`id`)
```

Another key thing to note here is that this action returns a dictionary which contains the `values()` results

```terminal
{'id': 2, 'title': 'Island Oasis - Raspberry', 'collection__title': 'Beauty'}
```

We can instead change the response to a tuple by using

```python
query_set = Product.objects.values_list('id', 'title', 'collection__title')
```

```terminal
(2, 'Island Oasis - Raspberry', 'Beauty')
```

### Challenge 1

Select all products that have been ordered and sort them by title.

We first find all items that have been ordered from the `OrderItem` table. We remove duplicates and use this to filter our `Products` table by searching for `Products.id` that are IN the `ordered_products` result set.

```python
ordered_products = OrderItem.objects.values('product__id').distinct()
query_set = Product.objects.filter(id__in=ordered_products)
```

### Using Only() to get Fields

```python
query_set = Product.objects.only('id', 'title')
```

This can be beneficial for performance reasons if you only need those specific fields and don't want to fetch all the other fields associated with the Product model from the database.

**HOWEVER**, we need to be careful with `only()` because if we reference a field that is NOT included in the `only()` function, we will force the execution of multiple individual queries to our database causing massive performance hits.

For example, if we reference `unit_price` for each product, we'd get 1002 queries sent to the database.

```jinja-html
{{p.title}} - {{p.unit_price}}
```

### Deferring Fields

We can perform the opposite of `only()` by leveraging `defer()`. This function can be used on text intensive or compute expensive columns to omit them from our query set.

```python
query_set = Product.objects.defer('description')
```

The same warning applies here as with `only()`.

### Selecting Related Objects

For this scenario, we'd like to capture the relationship between `Product` and `Collection`.

Specifically, we'd like to render the `Product.title` and `Collection.title` of that product. To do this, we use the `select_related()` method. This method is for 1 to 1 relationships. That is, each Product belongs to one collection.

One side note is that we can traverse relationships so if we have another relationship with `FooClass` and we wanted to join `Product`, `Collection` and `FooClass` we use:

```python
query_set = Product.objects.select_related('collection__fooClass').all()
```

Essentially, what we are doing here is "pre-loading" our Product query set with the related data from Collection.

```python
def say_hello(request):
    #  query_set are lazy evaluated
    query_set = Product.objects.select_related('collection').all()
    res = {'name': 'Mosh', 'products': list(query_set)}
    return render(request, 'hello.html', res)
```

In the frontend we display our results using

```html
<ul>
  {% for p in products %}
    <li>
    {{p.title}}  - {{p.collection.title}}
    </li>
  {% endfor %}
</ul>
```

If we don't access related object this way, we'd get performance hits because for each Product, a query will get sent to the database to get its `product.collection.title`.

For example, only using `all()`

```python
query_set = Product.objects.all()
```

But calling `collection.title` would negatively affect our performance.

```html
<ul>
  {% for p in products %}
    <li>
    {{p.title}}  - {{p.collection.title}}
    </li>
  {% endfor %}
</ul>
```

When there are many relationships such as Product and Promotions we use the `prefetch_related()` method.

In our Model definition this will look like a `models.ManyToManyField(Promotion)` field declaration. So, in order to render a Product and all of its promotions we use `prefetch_related()`.

```python
query_set = Product.objects.prefetch_related('promotions').all()
```

This SQL compiles to a 2 step process.

First, we read all products from the `store_product` table and then we use the `id` from this table to filter the `store_promotion`.

```sql
SELECT `store_product`.`id`,
       `store_product`.`title`,
       `store_product`.`slug`,
       `store_product`.`description`,
       `store_product`.`unit_price`,
       `store_product`.`inventory`,
       `store_product`.`last_update`,
       `store_product`.`collection_id`
  FROM `store_product`
```

```SQL
SELECT (`store_product_promotions`.`product_id`) AS `_prefetch_related_val_product_id`,
       `store_promotion`.`id`,
       `store_promotion`.`description`,
       `store_promotion`.`discount`
  FROM `store_promotion`
 INNER JOIN `store_product_promotions`
    ON (`store_promotion`.`id` = `store_product_promotions`.`promotion_id`)
 WHERE `store_product_promotions`.`product_id` IN (1, 2, 3,....)
```

We can also combine `prefetch_related()` and `select_related()` if we wish to get all Products, their collection and promotions.

```python
query_set = Product.objects.prefetch_related('promotions').select_related('collection').all()
```

Since each method returns a query set, we can chain them as such to build complex queries.

### Challenge 2

Get the last 5 orders with their customer and items (incl product).

Step 1: We first get the last 5 orders and their customer.

Step 2: prefetch the orderitem relationship to get access to the product field from OrderItem.

```python
def say_hello(request):

    recent_orders = Order.objects.select_related(
        'customer').order_by('-placed_at')[:5]
    recent_orders = recent_orders.prefetch_related('orderitem_set__product')

    context = {'name': 'Mosh', 'orders': list(recent_orders)}

    return render(request, 'hello.html', context)
```

To display our results on the frontend, we need to first show all orders and their customer and then for each `orderitem` we display the name of each product that was in that order.

So two for loops are needed to capture the one-to-one relationship between `Order` and `Customer` and one-to-many relationship between `Order` and `OrderItem`.

```html
<ul>
    {% for order in orders %}
      <li>
      {{order.id}} - {{order.customer.first_name}}
      <br>
      {% for order_item in order.orderitem_set.all %}
          {{ order_item.product.title }}
      {% endfor %}
      </li>
    {% endfor %}
</ul>
```

### Django Expression BaseClass

[Read the docs](https://docs.djangoproject.com/en/5.0/ref/models/expressions/#query-expressions)

The following section will look at various Built-in Expressions.

### Aggregating Objects

[Read the Docs](https://docs.djangoproject.com/en/5.0/topics/db/aggregation/)

At a high level, aggregating occurs with various Class instances from the `from django.db.models import` import statement.

Count  the number of Products - for this, we need to make sure we count the primary key, because if we count a field that contains `Nulls` those records won't be counted.

```python
def say_hello(request):
    #  query_set are lazy evaluated

    result = Product.objects.aggregate(Count('id'))

    context = {'name': 'Mosh', 'result': result}

    # Render the template with the context data
    return render(request, 'hello.html', context)
```

The result from an Aggregate is a dictionary with the column + aggregate function applied as the key name and the result from the aggregate function as the value.

```text
{'id__count': 1000}
```

We can provide our own key name by naming the applied aggregate function.

```python
result = Product.objects.aggregate(my_count=Count('id'))
```

```text
{'my_count': 1000}
```

We can also call several aggregate functions in our `.aggregate()` function to return several metrics. Here, we are finding the count of product Id's and the min unit price of our Products.

```python
result = Product.objects.aggregate(
        my_count=Count('id'), min_product_price=Min('unit_price'))
```

The results are displayed as

```text
{'my_count': 1000, 'min_product_price': Decimal('1.06')}
```

If we want to present our data in a nicer way, we can access each value from `result` using dot notation.

```html
{{results.min_product_price}}
```

One final note is that Aggregates can be applied to any query set so we can first perform `filter()` operations, apply `JOINS`, traverse relationships and then aggregate our data.

### Aggregate Exercises

How many orders do we have?

```python
result = Order.objects.aggregate(
        my_count=Count('id'))
```

How many units of Product 1 have we sold? - Find all OrderItems that are Product Id = 1 and then sum up the quantity of those OrderItems.

```python
result = OrderItem.objects.filter(
        product__id=1).aggregate(units_sold=Sum('quantity'))
```

How many Orders has Customer 1 placed?

```python
result = Order.objects.filter(customer__id=1).aggregate(Count('id'))
```

### Annotating Objects

Annotating Objects: "Add additional attributes to our Objects while querying them."

[Read the Docs](https://docs.djangoproject.com/en/5.0/ref/models/querysets/#annotate)

Adding a new field to Customers called `is_new` to be `True`

```python
query_set = Customer.objects.annotate(is_new=Value(True))
```

```SQL
SELECT `store_customer`.`id`,
       `store_customer`.`first_name`,
       `store_customer`.`last_name`,
       `store_customer`.`email`,
       `store_customer`.`phone`,
       `store_customer`.`birth_date`,
       `store_customer`.`membership`,
       1 AS `is_new`
  FROM `store_customer`
```

### Calling Database Functions

Create a `full_name` field that calls our Database `CONCAT()` function.

```python
query_set = Customer.objects.annotate(
        full_name=Func(
            F('first_name'), Value(" "), F('last_name'),
            function='CONCAT'
        )
    )
```

```sql
SELECT `store_customer`.`id`,
       `store_customer`.`first_name`,
       `store_customer`.`last_name`,
       `store_customer`.`email`,
       `store_customer`.`phone`,
       `store_customer`.`birth_date`,
       `store_customer`.`membership`,
       CONCAT(`store_customer`.`first_name`, ' ', `store_customer`.`last_name`) AS `full_name`
  FROM `store_customer`
```

For this specific example we can leverage the `Concat` database function offered by Django.

[Database Function Docs](https://docs.djangoproject.com/en/5.0/ref/models/database-functions/)

```python
....
from django.db.models.functions import Concat


def say_hello(request):
    #  query_set are lazy evaluated

    query_set = Customer.objects.annotate(
        full_name=Concat('first_name', Value(" "), 'last_name')
    )

    context = {'name': 'Mosh', 'query_set': list(query_set)}

    # Render the template with the context data
    return render(request, 'hello.html', context)
```

### Grouping Data

Find the number of orders each Customer has placed.

Note that here, we don't use `order_set` as the variable to count, this would return an error. Instead, we use `order` because that is the field that is available to us....

```text
Cannot resolve keyword 'order_set' into field. 
```

```python
query_set = Customer.objects.annotate(
        orders_placed=Count('order')
    )
```

```sql
SELECT `store_customer`.`id`,
       `store_customer`.`first_name`,
       `store_customer`.`last_name`,
       `store_customer`.`email`,
       `store_customer`.`phone`,
       `store_customer`.`birth_date`,
       `store_customer`.`membership`,
       COUNT(`store_order`.`id`) AS `orders_placed`
  FROM `store_customer`
  LEFT OUTER JOIN `store_order`
    ON (`store_customer`.`id` = `store_order`.`customer_id`)
 GROUP BY `store_customer`.`id`
 ORDER BY NULL
```

### Working with Expression Wrapper

`ExpressionWrapper` surrounds another expression and provides access to properties, such as `output_field`, that may not be available on other expressions. `ExpressionWrapper` is necessary when using arithmetic on `F()` expressions with different types.

Otherwise, we could get the error

```text
Expression contains mixed types....you must set output_field. 
```

So, if we want to add a field to our `Product` class called `discounted_price` we mathematically need to take `unit_price` * 0.8. Because `unit_price` is a Decimal Field but 0.8 is a float, we need to use an ExpressionWrapper.

```python
def say_hello(request):
    #  query_set are lazy evaluated
    discounted_price = ExpressionWrapper(
        F('unit_price') * 0.8, output_field=DecimalField()
    )
    query_set = Product.objects.annotate(
        discounted_price=discounted_price
    )

    context = {'name': 'Mosh', 'query_set': list(query_set)}

    # Render the template with the context data
    return render(request, 'hello.html', context)
```

This SQL compiles to

```SQL
SELECT `store_product`.`id`,
       `store_product`.`title`,
       `store_product`.`slug`,
       `store_product`.`description`,
       `store_product`.`unit_price`,
       `store_product`.`inventory`,
       `store_product`.`last_update`,
       `store_product`.`collection_id`,
       (`store_product`.`unit_price` * 0.8e0) AS `discounted_price`
  FROM `store_product`
```

#### Annotating Exercises
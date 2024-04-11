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

But calling `collection.title`

```html
<ul>
  {% for p in products %}
    <li>
    {{p.title}}  - {{p.collection.title}}
    </li>
  {% endfor %}
</ul>
```

Would negatively affect our performance.

When there are many relationships such as Product and Promotions we use the `prefetch_related()` method.

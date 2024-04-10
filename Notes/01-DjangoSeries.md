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

### Challenge 1

Select all products that have been ordered and sort them by title.

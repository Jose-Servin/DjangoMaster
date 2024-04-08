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

### Creating empty migrations

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
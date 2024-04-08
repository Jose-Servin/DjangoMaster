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

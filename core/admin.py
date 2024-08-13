from django.contrib import admin
from core.models import User
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for the User model.

    Inherits from Django's default UserAdmin and overrides the `add_fieldsets`
    to include email, first name, and last name fields during user creation.

    Attributes:
    - add_fieldsets (tuple): Defines the layout and fields displayed in the add user form.
    """

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )


class TagInline(GenericTabularInline):
    """
    Inline admin for displaying tags associated with any object in a tabular format.

    Attributes:
    - model (Model): The TaggedItem model that this inline represents.
    - autocomplete_fields (list): Specifies fields with autocomplete functionality.
    """

    autocomplete_fields = ["tag"]
    model = TaggedItem


class CustomProductAdmin(ProductAdmin):
    """
    Custom admin for the Product model to include tag management.

    Inherits from the standard ProductAdmin but adds the TagInline to manage
    tags directly from the Product admin page.

    Attributes:
    - inlines (list): List of inline models to be displayed on the Product admin page.
    """

    inlines = [TagInline]


# Unregister the default Product admin and register the custom one
admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)

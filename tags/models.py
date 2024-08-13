from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.


class TaggedItemManager(models.Manager):
    """
    Custom manager for the TaggedItem model to provide additional querying capabilities.

    Methods:
    - get_tags_for(obj_type, obj_id): Retrieves all tags associated with a given object.
    """

    def get_tags_for(self, obj_type, obj_id):
        """
        Retrieve all tags associated with a specific object.

        Parameters:
        - obj_type (Model class): The model class of the object.
        - obj_id (int): The primary key of the object.

        Returns:
        - QuerySet: A queryset containing TaggedItem instances related to the given object.
        """
        content_type = ContentType.objects.get_for_model(obj_type)

        query_set = TaggedItem.objects.select_related("tag").filter(
            content_type=content_type, object_id=obj_id
        )
        return query_set


class Tag(models.Model):
    """
    Represents a label or tag that can be associated with different objects.

    Attributes:
    - label (str): The text of the tag.

    Methods:
    - __str__(): Returns the label of the tag.
    """

    label = models.CharField(max_length=255)

    def __str__(self) -> str:
        """Returns the label of the tag."""
        return self.label


class TaggedItem(models.Model):
    """
    Represents the relationship between a Tag and a specific object.

    Attributes:
    - tag (ForeignKey): The tag associated with the object.
    - content_type (ForeignKey): The type of the related object.
    - object_id (int): The ID of the related object.
    - content_object (GenericForeignKey): The actual object that the tag is associated with.

    Notes:
    - Uses a GenericForeignKey to allow tagging of any model instance.
    - Deleting an object will also delete all associated tags.
    - Assumes that the related object has an integer primary key.
    """

    objects = TaggedItemManager()
    # What tag is applied to what Object
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    # If this Object is deleted, delete all associated tags
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # LIMITATION: we are assuming each Object will have an ID field. This can break if it's a GUID.
    object_id = models.PositiveIntegerField()
    # This lets us know about the actual object a particular tag is applied to
    content_object = GenericForeignKey()

    """
    Summary:
    - **Tagging System**: This module provides a tagging system that allows any model instance to be tagged with one or more labels. The `TaggedItem` model establishes a relationship between a `Tag` and a specific object using `GenericForeignKey`, which means it can be applied to instances of any model.
    - **Custom Manager**: The `TaggedItemManager` class extends the default manager to include a method for retrieving tags associated with a specific object, making it easy to query tags in a more object-oriented way.
    - **Assumptions**: It assumes that all related objects have an integer-based primary key (which might be a limitation if you're using non-integer primary keys like GUIDs).
    """

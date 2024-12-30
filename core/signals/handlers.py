from django.dispatch import receiver
from store.signals import order_created


@receiver(order_created)
def on_order_created(sender, **kwargs):
    """
    Handle the order_created signal by sending a notification.
    """
    order = kwargs["order"]
    print(f"Order {order.id} created.")

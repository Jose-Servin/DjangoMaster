from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from . import views
from pprint import pprint

# Parent Router
router = routers.DefaultRouter()
# Products end point should be managed by the ProductViewSet
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)
router.register("carts", views.CartViewSet)
router.register("customers", views.CustomerViewSet)

# Product Nested Router
products_router = routers.NestedDefaultRouter(router, "products", lookup="product")

# Child Router of Product
products_router.register("reviews", views.ReviewViewSet, basename="product-reviews")

# Cart Nested Router
cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")

# Child Router of Cart
cart_router.register("items", views.CartItemViewSet, basename="cart-items")

urlpatterns = router.urls + products_router.urls + cart_router.urls

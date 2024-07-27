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

# Product Nested Router
products_router = routers.NestedDefaultRouter(
    router, "products", lookup="product")

# Child Router of Product
products_router.register("reviews", views.ReviewViewSet,
                         basename="product-reviews")

urlpatterns = router.urls + products_router.urls

from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views
from pprint import pprint


router = SimpleRouter()
# Products end point should be managed by the ProductViewSet
router.register("products", views.ProductViewSet)
router.register("collections", views.CollectionViewSet)

urlpatterns = router.urls

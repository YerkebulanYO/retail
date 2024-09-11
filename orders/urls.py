from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderProductDetailView
from django.urls import path, include

router = DefaultRouter()
router.register(r'orders', OrderViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('orders/<int:order_pk>/products/<int:id>/', OrderProductDetailView.as_view(), name='order-product-detail'),
]

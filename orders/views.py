from datetime import datetime, timezone

from django.db.models import Sum, Q
from rest_framework import viewsets, generics, status
from rest_framework import decorators as drf_decorators
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from products.models import Product
from .models import Order, OrderProduct
from .serializers import OrderSerializer, OrderProductDetailSerializer, StatisticsQuerySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date for the range (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date for the range (YYYY-MM-DD)", type=openapi.TYPE_STRING)
        ],
    )
    @drf_decorators.action(detail=False, methods=["GET"])
    def statistics(self, request):
        serializer = StatisticsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        # Преобразуем в datetime с временной зоной (timezone-aware)
        start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

        # Арендная сумма для каждого продукта
        rental_statistics = OrderProduct.objects.filter(
            Q(order__start_date__gte=start_datetime) &
            Q(order__end_date__lte=end_datetime)
        ).values('product__name').annotate(total_rental_amount=Sum('rental_price'))

        # Таблица доступных периодов для каждого продукта
        all_products = Product.objects.all()
        available_intervals = {}

        for product in all_products:
            orders = OrderProduct.objects.filter(
                product=product,
                order__end_date__gte=start_datetime,
                order__start_date__lte=end_datetime
            ).order_by('order__start_date')

            available_periods = []
            previous_end_date = start_datetime

            for order_product in orders:
                if order_product.order.start_date > previous_end_date:
                    available_periods.append({
                        "start": previous_end_date.isoformat(),
                        "end": order_product.order.start_date.isoformat()
                    })
                previous_end_date = order_product.order.end_date

            if previous_end_date < end_datetime:
                available_periods.append({
                    "start": previous_end_date.isoformat(),
                    "end": end_datetime.isoformat()
                })

            available_intervals[product.name] = available_periods

        return Response({
            'rental_statistics': list(rental_statistics),
            'available_intervals': available_intervals
        })

class OrderProductDetailView(generics.RetrieveAPIView):
    serializer_class = OrderProductDetailSerializer
    lookup_field = 'id'

    def get_queryset(self):
        order_pk = self.kwargs['order_pk']
        order_product_pk = self.kwargs['id']
        return OrderProduct.objects.filter(order_id=order_pk, id=order_product_pk)

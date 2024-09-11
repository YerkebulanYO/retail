from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _
from django.db import transaction

from products.models import Product
from products.serializers import ProductSerializer
from .models import Order, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = ['product', 'rental_price', 'rental_duration_days']


class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['start_date', 'end_date', 'order_products']

    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        order_products_data = data['order_products']

        date_difference_days = (end_date - start_date).days

        for item in order_products_data:
            rental_duration_days = item['rental_duration_days']
            if rental_duration_days > date_difference_days:
                raise ValidationError(_("The rental duration for product {product} exceeds the available rental period.").format(product=item['product']))

        # Проверяем, что один продукт не включен более одного раза
        product_ids = [item['product'] for item in order_products_data]
        if len(product_ids) != len(set(product_ids)):
            raise ValidationError(_("A product cannot be included in the same order more than once."))

        # Проверяем пересечение аренды
        for item in order_products_data:
            product = item['product']
            overlapping_orders = OrderProduct.objects.filter(
                product=product,
                order__end_date__gte=start_date,
                order__start_date__lte=end_date
            )

            if self.instance and self.instance.id:
                overlapping_orders = overlapping_orders.exclude(order__id=self.instance.id)

            if overlapping_orders.exists():
                raise ValidationError(_("There are overlapping orders for the same product."))

        return data

    @transaction.atomic
    def create(self, validated_data):
        order_products_data = validated_data.pop('order_products')

        total_price = 0

        for order_product_data in order_products_data:
            rental_price = order_product_data['rental_price']
            rental_duration_days = order_product_data['rental_duration_days']
            total_price += rental_price * rental_duration_days

        order = Order.objects.create(total_price=total_price, **validated_data)
        for order_product_data in order_products_data:
            OrderProduct.objects.create(order=order, **order_product_data)

        return order


class OrderProductDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderProduct
        fields = '__all__'


class StatisticsQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
from django.db import models
from products.models import Product
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    def __str__(self):
        return f'Order {self.id} from {self.start_date} to {self.end_date}'

    def calculate_total_price(self):
        total = sum(item.calculate_price() for item in self.order_products.all())
        self.total_price = total
        self.save()

    def clean(self):
        super().clean()
        self.validate_non_overlapping_products()

    def validate_non_overlapping_products(self):
        for item in self.order_products.all():
            conflicting_orders = OrderProduct.objects.filter(
                product=item.product,
                order__end_date__gte=self.start_date,
                order__start_date__lte=self.end_date,
            ).exclude(order=self)

            if conflicting_orders.exists():
                raise ValidationError(_(f'Product {item.product} is already rented in another order during this period.'))


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='order_products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_products', on_delete=models.CASCADE)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_duration_days = models.PositiveIntegerField()

    class Meta:
        unique_together = ('order', 'product')

    def __str__(self):
        return f'{self.product.name} in Order {self.order.id}'

    def calculate_price(self):
        return self.product.price * self.rental_duration_days
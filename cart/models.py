from adminside.models import Custom_user
from django.db import models
from products.models import *


# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(blank=True, max_length=250)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.cart_id


class Cartitem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    size = models.CharField(null=True, max_length=25)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return self.product.product_name

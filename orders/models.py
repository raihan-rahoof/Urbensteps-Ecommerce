from django.contrib.auth.models import User
from django.db import models
from products.models import *


# Create your models here.


class Order(models.Model):
    STATUS = (
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Deliverd", "Deliverd"),
        ("Cancel", "Cancel"),
        ("Return", "Return"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.CharField(null=True, max_length=50, blank=True)
    payment_status = models.CharField(null=True, max_length=50, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, default="not available")
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    hometown = models.CharField(max_length=50)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default="New")
    ip = models.CharField(blank=True, max_length=80)
    is_ordered = models.BooleanField(default=False)
    soft_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"order of {self.user.username} on {self.created_at}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    status = models.CharField(max_length=100, default="None")
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name


class onlinePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True,blank=True)
    payment_id = models.CharField(max_length=50, null=True)
    payment_method = models.CharField(max_length=50, null=True)
    amount_paid = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self) -> str:
        return self.payment_id


class Cancelorder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    order_product = models.ForeignKey(
        OrderProduct, on_delete=models.CASCADE, blank=True, null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CancelReason for OrderProduct {self.user.username}"


class Coupons(models.Model):
    name = models.CharField(max_length= 50)
    description = models.TextField()
    image = models.ImageField(upload_to='coupons/',default="no images found")
    code = models.CharField(max_length=50)  
    discount = models.PositiveIntegerField()
    min_amount = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    coupon = models.ForeignKey(Coupons, on_delete=models.CASCADE,null=True)
    code = models.CharField(max_length=50)
    total_amount = models.BigIntegerField(null=True,blank=True)
    discount_amount = models.BigIntegerField(null=True,blank=True)
    used = models.BooleanField()
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(null=True)
    valid_to = models.DateField(null=True)
    usage_time = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user} used {self.coupon.name}"


class OrderReturn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True , blank=True)
    order_product = models.ForeignKey(OrderProduct, on_delete=models.CASCADE,null=True , blank=True)
    amount = models.PositiveIntegerField()
    option = models.CharField(null=True, max_length=50)
    reason = models.TextField(null=True)
    collected = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username
    


    
    
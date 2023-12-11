from django.contrib.auth.models import User
from django.db import models
from offers.models import *

# Create your models here.


class Category(models.Model):
    name = models.CharField(null=True, max_length=50)
    description = models.CharField(null=True, max_length=50)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    name = models.CharField(null=True, max_length=50)
    description = models.CharField(null=True, max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Custom_user(User):
    gender = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    refferal_code = models.CharField(unique=True, max_length=50, null=True)
    refferer = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_block = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.username

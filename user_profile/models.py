from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class User_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=25, blank=True, null=True)
    mobile_number = models.TextField(null=True, blank=True)
    profile = models.ImageField(
        upload_to="profile/", default="No images available", blank=True, null=True
    )

    def __str__(self) -> str:
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    district = models.CharField(max_length=255, null=True, blank=True)
    hometown = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"wallet of {self.user.username}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True)
    transaction = models.CharField(null=True, max_length=50)
    made_on = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"transaction of {self.wallet.user.username}"

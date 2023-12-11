from decimal import Decimal

from adminside.models import *
from django.db import models
from django.db.models import Avg, Count
from offers.models import *
from user_profile.models import *


# Create your models here.
class Products(models.Model):
    product_name = models.CharField(unique=True, max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True
    )  # foriegn key
    subcategory = models.CharField(null=True, max_length=50)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    stock = models.IntegerField()
    sizes = models.CharField(null=True, max_length=50)
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True
    )  # foriegn key
    price = models.DecimalField(max_digits=10, decimal_places=2)
    return_time = models.CharField(default="Return not available", max_length=50)
    meterial = models.CharField(default="NA", max_length=200)
    warranty = models.CharField(default="NA", max_length=50)
    image = models.ImageField(
        upload_to="products/", default="No images available", blank=True
    )
    special = models.BooleanField(default=False)
    offer_pro = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.product_name

    def get_offer(self):
        product_offer = self.offer
        category_offer = self.category.offer

        if (
            product_offer
            and not product_offer.is_offer_expired()
            and category_offer
            and not category_offer.is_offer_expired()
        ):
            max_discount = max(
                Decimal(product_offer.discount), Decimal(category_offer.discount)
            )
            discount = (max_discount / Decimal(100)) * Decimal(self.price)
            discount_amount = Decimal(self.price) - discount
            return float(discount_amount)

        elif product_offer and not product_offer.is_offer_expired():
            discount = (Decimal(product_offer.discount) / Decimal(100)) * Decimal(
                self.price
            )
            discount_amount = Decimal(self.price) - discount
            return float(discount_amount)

        elif category_offer and not category_offer.is_offer_expired():
            discount = (Decimal(category_offer.discount) / Decimal(100)) * Decimal(
                self.price
            )
            discount_amount = Decimal(self.price) - discount
            return float(discount_amount)

        else:
            return float(self.price)

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(
            average=Avg("rating")
        )
        avg = 0
        if reviews["average"] is not None:
            avg = float(reviews["average"])
            return avg

    def count_reviews(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(
            count=Count("rating")
        )
        count = 0
        if reviews["count"] is not None:
            count = int(reviews["count"])
        return count


class MultipleImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    images = models.ImageField(
        upload_to="products/", default="No images available", blank=True
    )

    def __str__(self) -> str:
        return f"Image for {'self.product.product_name'}"


class ReviewRating(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(User_profile, on_delete=models.CASCADE)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(blank=True, max_length=50)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s review on {self.product.product_name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"whishlist of {self.user.username}"

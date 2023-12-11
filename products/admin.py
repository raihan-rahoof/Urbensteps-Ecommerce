from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Products)
admin.site.register(MultipleImage)
admin.site.register(ReviewRating)
admin.site.register(Wishlist)

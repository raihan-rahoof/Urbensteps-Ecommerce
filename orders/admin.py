from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderProduct)

admin.site.register(onlinePayment)
admin.site.register(Coupons)
admin.site.register(CouponUsage)
admin.site.register(OrderReturn)



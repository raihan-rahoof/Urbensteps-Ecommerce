from django.contrib import admin
from django.urls import path,include
from . import views

app_name = 'coupons'

urlpatterns = [
    path('', views.coupons ,name="coupons"),
    path('add_coupon/', views.add_coupon ,name="add_coupon"),
    path('edit_coupon/<int:id>/', views.edit_coupon ,name="edit_coupon"),
    path('delete_coupon/<int:id>/', views.delete_coupon ,name="delete_coupon"),
    path('disable_coupon/<int:id>/', views.disable_coupon ,name="disable_coupon"),

   
]
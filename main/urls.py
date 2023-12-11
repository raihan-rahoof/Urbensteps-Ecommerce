from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("details/<int:id>/", views.product_details, name="product_details"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
]

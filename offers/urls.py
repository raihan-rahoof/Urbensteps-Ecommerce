from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "offers"

urlpatterns = [
    path("", views.offers, name="offers"),
    path("add_offer/", views.add_offer, name="add_offer"),
    path("update_offer/<int:id>/", views.update_offer, name="update_offer"),
    path("delete_offer/<int:id>/", views.delete_offer, name="delete_offer"),
]

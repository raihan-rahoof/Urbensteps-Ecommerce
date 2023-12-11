from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "products"

urlpatterns = [
    path("manage_products/", views.manage_products, name="manage_products"),
    path("add_products/", views.add_products, name="add_products"),
    path("edit_products/<int:id>/", views.edit_product, name="edit_products"),
    path("update_product/<int:id>/", views.update_product, name="update_product"),
    path("remove_product/<int:id>/", views.remove_product, name="remove_product"),
    path("delete_product/<str:id>/", views.delete_product, name="delete_product"),
    path("view_product/<int:id>/", views.view_product, name="view_product"),
]

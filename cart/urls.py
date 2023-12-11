from django.urls import include, path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add_cart/<int:id>/", views.add_cart, name="add_cart"),
    path("remove_cart/<int:id>/", views.remove_cart, name="remove_cart"),
    path("delete_cart_item/<int:id>/", views.delete_cart_item, name="delete_cart_item"),
    path("update_cart/", views.update_cart, name="update_cart"),
]

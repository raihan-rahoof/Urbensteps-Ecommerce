from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "user_profile"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("address/", views.address, name="address"),
    path("add-address/", views.add_address, name="add_address"),
    path("delete_address/<int:id>/", views.delete_address, name="delete_address"),
    path("update_address/<int:id>/", views.update_address, name="update_address"),
    path("order-track/", views.order_track, name="order-track"),
    path(
        "cancel-product/<int:id>/<int:oid>/",
        views.cancel_product,
        name="cancel_product",
    ),
    path("cancel-order/<int:id>/", views.cancel_order, name="cancel_order"),
    path("remove-order/<int:id>/", views.remove_order, name="remove_order"),
    path("rewards/", views.rewards, name="rewards"),
    path("wallet/", views.wallet, name="wallet"),
    path("return-page/<int:id>/", views.return_page, name="return_page"),
    path("return-order/<int:id>/", views.return_order, name="return_order"),
    path("return-orders/", views.returnorder_page, name="returned_page"),
    path("view-returns/<int:id>/", views.view_returns, name="view_returns"),
    path("approve-return/<int:id>/", views.approve_return, name="approve_return"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add-to-wishlist/<int:id>/", views.add_wishlist, name="add_wishlist"),
    path("remove-wishlist/<int:id>/", views.remove_wishlist, name="remove_wishlist"),
]

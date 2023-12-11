from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "userauth"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("register/", views.user_register, name="register"),
    path("otp/", views.verify_otp, name="otp"),
    path("logout/", views.user_logout, name="logout"),
    path("social/signup/", views.signup_redirect, name="signup_redirect"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path(
        "resetpassword-validate/<str:uidb64>/<str:token>/",
        views.resetpassword_validate,
        name="resetpassword_validate",
    ),
    path("reset-password/", views.reset_password, name="reset_password"),
]

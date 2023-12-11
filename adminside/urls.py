from django.urls import include, path

from . import views

app_name = "adminside"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cadmin_login/", views.cadmin_login, name="cadmin_login"),
    path("cadmin_logout/", views.cadmin_logout, name="cadmin_logout"),
    path("users_management/", views.users_mgmt, name="users_mgmt"),
    path("user_block/<int:user_id>/", views.user_block, name="user_block"),
    path("user_unblock/<int:user_id>/", views.user_unblock, name="user_unblock"),
    path("list_category/", views.list_category, name="list_category"),
    path("add_category/", views.add_category, name="add_category"),
    path("delete_category/<str:id>/", views.delete_category, name="delete_category"),
    path("show/<int:id>", views.show, name="show"),
    path("update_category/<int:id>/", views.update_category, name="update_category"),
    path("list_brand/", views.list_brand, name="list_brand"),
    path("add_brand/", views.add_brand, name="add_brand"),
    path("delete_brand/<str:id>/", views.delete_brand, name="delete_brand"),
    path("show_brand/<int:id>", views.show_brand, name="show_brand"),
    path("update_brand/<int:id>/", views.update_brand, name="update_brand"),
    path("sales-report/", views.sales_report, name="sales_report"),
    path("sales-report-pdf/", views.sales_report_pdf, name="sales_report_pdf"),
]

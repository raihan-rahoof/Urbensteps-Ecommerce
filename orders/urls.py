from django.contrib import admin
from django.urls import path,include
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.checkout ,name="checkout"),
    path('place_order/', views.place_order ,name="place_order"),
    path('coupon-applied/', views.apply_coupon ,name="apply_coupon"),
    path('list_order/', views.list_order ,name="list_orders"),
    path('change-status/<int:id>/', views.change_status ,name="change_status"),
    path('view-order/<int:id>/', views.view_order, name="view_order"),
    path('remove/<int:id>/', views.soft_remove, name="soft_remove"),
    path('delete/<int:id>/', views.order_delete, name="order_delete"),
    path('place-order/', views.place_order,name="online_payment"),
    path('online-payment/', views.online_payment ,name="online_payment_sucsses"),
    path('order-succssesfull/', views.order_sucsses ,name="order_sucsses"),
    path('submit-review/<int:id>/', views.submit_review ,name="submit_review"),
    

    

    
    
]
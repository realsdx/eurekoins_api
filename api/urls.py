from django.urls import path
from api import views

appname="api"

urlpatterns = [
    path('register/', views.register_user, name="register"),
    path('exists/', views.check_user_exists, name="exists"),
    path('users/', views.get_user_list, name="user_list"),
    path('invite_code/', views.get_invite_code, name="invite_code"),
    path('transfer/', views.transfer_coin, name="transfer"),
    path('coupon/', views.redeem_coupon, name="redeem_coupon")
]

from django.urls import path
from api import views

appname="api"

urlpatterns = [
    path('register/', views.register_user, name="register"),
    path('exists/', views.check_user_exists, name="exists"),
    path('users/', views.get_user_list, name="user_list"),
]

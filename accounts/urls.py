from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('<str:username>', views.user_by_username, name='user_list'),
]

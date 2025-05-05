from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_convo, name='start_convo'),
    path('get_unread_messages/<int:convo_id>', views.get_unread_messages, name='get_unread_messages'),
    path('<int:convo_id>/', views.get_conversation, name='get_conversation'),
    path('', views.conversations, name='conversations')
]

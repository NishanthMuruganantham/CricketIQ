from django.urls import path
from .views import ChatView

urlpatterns = [
    path('ask/', ChatView.as_view(), name='chat-ask'),
]

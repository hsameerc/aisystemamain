from django.urls import re_path
from support_app import chat

websocket_urlpatterns = [
    re_path(r"ws/chat/$", chat.Chat.as_asgi()),
]

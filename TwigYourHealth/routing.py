from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.urls import path

from communication.consumers import ChatConsumer, CallConsumer

application = ProtocolTypeRouter({

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path(r"chat/<int:user_id>/", ChatConsumer),
            path(r"call/", CallConsumer),
        ])
    ),
})

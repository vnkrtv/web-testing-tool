import os

from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from main.consumers import RunningTestsConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(os.getenv('URL_PREFIX', '') + r'^available_tests/$', RunningTestsConsumer.as_asgi()),
                ]
            )
        )
    )
})

from django.urls import path
from match_app.services.match_consumer import MatchConsumer

websocket_urlpatterns = [
    path(
        "ws/match/<int:matchId>/", MatchConsumer.as_asgi()
    ),
]

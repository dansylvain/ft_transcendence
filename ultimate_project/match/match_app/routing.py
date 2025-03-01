from django.urls import path
from match_app.services.consumer import (
    MyConsumer,
)  # Remplacez 'votre_app' par le nom de votre app..

websocket_urlpatterns = [
    path(
        "ws/match/<int:match_id>/", MyConsumer.as_asgi()
    ),  # Définit le chemin d'accès au websocket
]

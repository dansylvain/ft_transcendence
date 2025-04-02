from django.urls import path
from tournament_app.services.simple_match_consumer import SimpleConsumer 
from tournament_app.services.tournament_consumer import TournamentConsumer
from django.urls import re_path

websocket_urlpatterns = [
    path(
		"ws/tournament/simple-match/<int:user_id>/<str:user_name>/",
		SimpleConsumer.as_asgi()),
    re_path(
		r"^ws/tournament/tournament/"
		r"(?P<user_id>-?\d+)/(?P<user_name>\w+)/$",
		TournamentConsumer.as_asgi())
]

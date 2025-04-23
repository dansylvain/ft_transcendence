from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PlayerViewSet, TournamentViewSet, MatchViewSet, PlayerStatisticsViewSet

from . import views
# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'player', PlayerViewSet)
router.register(r'tournament', TournamentViewSet)
router.register(r'match', MatchViewSet)
router.register(r'player_stats', PlayerStatisticsViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/verify-credentials/', views.verify_credentials, name="verify_credentials"),
    path('api/check-2fa/', views.check_2fa, name="check_2fa"),
    #! DO NOT APPEND TRAILING SLASH TO UUID - damm DO NOT APPEND SLASH
    path('api/player/<int:player_id>/uuid', views.uuid, name="uuid_view"),
    
    #API endpoint for custom action for stats
    path('api/player/<int:player_id>/stats/update-stats/', PlayerStatisticsViewSet.as_view({'post': 'update_stats'})),
    path('api/player/stats/get-top-players/', PlayerStatisticsViewSet.as_view({'get': 'get_top_players'})),
    
]
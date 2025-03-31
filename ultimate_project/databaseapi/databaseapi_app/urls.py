from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PlayerViewSet, TournamentViewSet, MatchViewSet

from . import views
# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'player', PlayerViewSet)
router.register(r'tournament', TournamentViewSet)
router.register(r'match', MatchViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/', include(router.urls)),
    
    path('api/verify-credentials/', views.verify_credentials, name="verify_credentials"),
    
    path('api/check-2fa/', views.check_2fa, name="check_2fa"),
]
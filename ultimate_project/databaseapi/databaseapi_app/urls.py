from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PlayerViewSet, TournamentViewSet, MatchViewSet

from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"player", PlayerViewSet)
router.register(r"tournament", TournamentViewSet)
router.register(r"match", MatchViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/verify-credentials/", views.verify_credentials, name="verify_credentials"
    ),
    path("api/register/", views.register, name="register"),
    path("api/token/refresh/", views.refresh_token, name="refresh_token"),
    path("api/token/verify/", views.verify_token, name="verify_token"),
    path("api/user-from-token/", views.user_from_token, name="user_from_token"),
    path("api/enable-2fa/", views.enable_2fa, name="enable_2fa"),
    path("api/verify-2fa-setup/", views.verify_2fa_setup, name="verify_2fa_setup"),
]

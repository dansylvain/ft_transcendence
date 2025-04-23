from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.conf import settings

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("home/", views.home),
    path("reload-template/", views.reload_template, name="reload_template"),
    path(
        "tournament-match-wrapper/<str:user_id>/",
        views.match_simple_template,
        name="tournament_match_wrapper",
    ),
    path(
        "tournament-wrapper/<str:user_id>/",
        views.tournament_template,
        name="tournament_wrapper",
    ),
    path("translations/<str:lang>.json", views.translations, name="translations"),
    path("register/", views.register, name="register"),
    path("two-factor-auth/", views.twoFactorAuth, name="login"),
    path("error/<int:code>/", views.error, name="error"),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico', permanent=True)),
]

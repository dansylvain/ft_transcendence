from django.urls import path
from .views.login import login_view
from .views.logout import logout_view
from .views.register import register_view


urlpatterns = [
    path("login/", login_view.login_view, name="login"),
    path("logout/", logout_view.logout_view, name="logout"),
    path("register/", register_view.register_view, name="register"),
]

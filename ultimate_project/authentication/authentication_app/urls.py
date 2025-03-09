from django.urls import path

from . import views

# from . import two_fa

urlpatterns = [
    # path("", views.index, name="auth_index"),
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("refresh-token/", views.refresh_token_view, name="refresh_token"),
    path("setup-2fa/", views.setup_2fa_view, name="setup_2fa"),
    path("verify-2fa-setup/", views.verify_2fa_setup_view, name="verify_2fa_setup"),
]

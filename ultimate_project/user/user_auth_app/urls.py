from django.urls import path
from .views import login_view, logout_view, register_view, forgot_password


urlpatterns = [
    path("login/", login_view.login_view, name="login"),
    path("logout/", logout_view.logout_view, name="logout"),
    path("register/", register_view.register_view, name="register"),
    path("forgot-password/", forgot_password.forgot_password_view, name="forgot_password"),
    
]

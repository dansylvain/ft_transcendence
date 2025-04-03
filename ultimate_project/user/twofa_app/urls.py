from django.urls import path
from . import views

urlpatterns = [
    path("setup-2fa/", views.setup_2fa, name="setup_2fa"),
    path("verify-2fa/", views.verify_2fa, name="verify_2fa"),
    path("disable-2fa/", views.disable_2fa, name="disable_2fa"),
]

from django.urls import path

from .views.login import login_view
from .views.logout import logout_view
from .views.register import register_view


urlpatterns = [
   
    path("/login/", login_view.login_view, name="login"),

    path("/logout/", logout_view.logout_view, name="logout"),
    
    path("/register/", register_view.register_view, name="logout"),
    
    
    
    #path("verify-2fa/", views.verify_2fa, name="verify_2fa"),
    #path("disable-2fa/", views.disable_2fa, name="disable_2fa"),
]

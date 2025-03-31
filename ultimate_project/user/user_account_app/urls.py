from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async, async_to_sync
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from .views.profile import profile_view
from .views.game_stats import game_stats_view
from .views.security.password import password_views
from .views.security.twofa import twofa_views


urlpatterns = [

    path("/profile/", profile_view.show_profile, name="profile"),
    path("/game-stats/", game_stats_view.game_stats_view, name="game-stats"),
    
    #path("/security/", )
    path("/security/setup-2fa/", twofa_views.setup_2fa),
    path("/security/verify-2fa/", twofa_views.verify_2fa),
    path("/security/disable-2fa/", twofa_views.disable_2fa),
    
    
    #path("delete-profile/", views.delete_profile_view, name="delete_profile"),
    

]

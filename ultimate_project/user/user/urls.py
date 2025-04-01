from django.urls import path, include
from django.http import HttpResponse, JsonResponse

import user_account_app.views as user_account_views
import twofa_app.views as twofa_views
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async, async_to_sync
from django.views.decorators.http import require_http_methods, require_POST, require_GET


# Create a view that doesn't get logged
@csrf_exempt
def health_check(request):
    return HttpResponse(status=200)


urlpatterns = [
    path("health/", health_check, name="health_check"),
    # path("debug-headers/", debug_headers, name="debug_headers"),
    
    # Eevrythign related to account management
    path("account/", include("user_account_app.urls"), name="account"),
    # login, register, logout
    path("auth/", include("user_auth_app.urls"), name="auth"),

    #path("user/setup-2fa/", async_to_sync(twofa_views.setup_2fa)),
    #path("user/verify-2fa/", async_to_sync(twofa_views.verify_2fa)),
    #path("user/disable-2fa/", async_to_sync(twofa_views.disable_2fa)),
    
    
    # base url when going into your account
   
    
    #Preparing urls for account manager
    # 1 -  account info / 2 - Security / 
    # 3 - game stat
    # 4 - Confidentialité (show if connected or not / accept firend request or not
    # delete account)
    
    
    
   
]

from django.urls import path, include
from django.http import HttpResponse, JsonResponse

import user_account_app.views as user_account_views
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
    
    # Everythin related to account management
    path("account/", include("user_account_app.urls"), name="account"),
   
]

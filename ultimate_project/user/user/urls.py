from django.urls import path, include
from django.http import HttpResponse, JsonResponse
import user_app.views as views
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
    path("user/", include("user_management_app.urls")),
    path("user/profile/", views.profile),
    path("user/stats/", views.stats),
    path("user/setup-2fa/", async_to_sync(twofa_views.setup_2fa)),
    path("user/verify-2fa/", async_to_sync(twofa_views.verify_2fa)),
    path("user/disable-2fa/", async_to_sync(twofa_views.disable_2fa)),
]

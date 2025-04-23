from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Create a view that doesn't get logged
@csrf_exempt
def health_check(request):
    return HttpResponse(status=200)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),
    path("", include("databaseapi_app.urls")),  # Include our app's URLs
]

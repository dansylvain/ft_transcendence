"""
URL configuration for match project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
import match_app.views as views
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import re_path

@csrf_exempt
def health_check(request):
    return HttpResponse(status=200)

urlpatterns = [
    path("health/", health_check, name="health_check"), 
	path("match/new-match/", views.new_match),
    path("match/match2d/", views.enter_match2d),
    path("match/match3d/", views.enter_match3d),
    re_path(
		r"^match/stop-match/(?P<playerId>-?\d+)/(?P<matchId>-?\d+)/$",
		views.stop_match
    )
]

"""
URL configuration for tournament project.

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
import tournament_app.views as views
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    return HttpResponse(status=200)

urlpatterns = [
    path("health/", health_check, name="health_check"), 
    
	path("tournament/simple-match/<int:user_id>/", views.simple_match),  	
    path("tournament/match-players-update/", views.match_players_update),  
	path("tournament/match-result/", views.match_result), 
       
	path("tournament/tournament/<int:user_id>/", views.tournament),
    path(
        "tournament/tournament-pattern/<int:tournament_id>/",
        views.tournament_pattern
    ),
]


import os
import httpx
import pyotp
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import cache_control

from utils import manage_user_data


#@cache_control(no_cache=True, must_revalidate=True)
async def game_stats_view(request: HttpRequest):
    
    username = request.headers.get("X-Username")

    context = {
        "rasp": os.getenv("rasp", "false"),
        "pidom": os.getenv("pi_domain", "localhost:8443"),
    }

    if username:
        user = await manage_user_data.get_user_info_w_username(username)
        if user:
            context["user"] = user

    if request.headers.get("HX-Request"):
        # Check for custom header indicating inner content request
        if request.headers.get("X-Inner-Content") == "true":
                return render(request, "partials/game_stats/game_stats.html", context)
            
    return render(request, "layouts/account.html", {
        "username": username,
        "page": "partials/game_stats/game_stats.html",
        **context
    })
    

import os
import httpx
import pyotp
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import cache_control

from utils import get_user_info_w_username


#@cache_control(no_cache=True, must_revalidate=True)
async def game_stats_view(request: HttpRequest):
    
    username = request.headers.get("X-Username")

    context = {
        "rasp": os.getenv("rasp", "false"),
        "pidom": os.getenv("pi_domain", "localhost:8443"),
    }

    if username:
        user = await get_user_info_w_username(username)
        if user:
            context["user"] = user

    if request.headers.get("HX-Request"):
        # Check for custom header indicating inner content request
        if request.headers.get("X-Inner-Content") == "true":
            # Only return the inner content (profile or game stats)
            if "/user/account/game-stats/" in request.path:
                return render(request, "partials/stats.html", context)
            
    return render(request, "account.html", {
        "username": username,
        "page": "partials/stats.html",
        **context
    })
    

import os
import httpx
import pyotp
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import cache_control

from utils import utils_user_auth

async def logout_view(request: HttpRequest):
    return await utils_user_auth.logout_api(request)

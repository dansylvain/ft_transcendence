# import os
# import httpx
# import pyotp
from django.http import HttpRequest, JsonResponse
# from django.shortcuts import render
# from django.template.loader import render_to_string
# from django.views.decorators.http import require_http_methods
# from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
# from django.views.decorators.cache import cache_control

from utils import utils_user_auth

async def register_view(request: HttpRequest):
    form_data = await request.form()  # Extract form data

    first_name = form_data.get("first_name")
    last_name = form_data.get("last_name")
    username = form_data.get("username")
    password = form_data.get("password")
    email = form_data.get("email")
    # Create a new response object

    return await utils_user_auth.register_api(
        username, password, email, first_name, last_name
    )

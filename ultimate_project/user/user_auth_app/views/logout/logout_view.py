from django.shortcuts import render
import json
import os
from itsdangerous import URLSafeTimedSerializer
# from django.http import HttpResponseBadRequest
from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache
from utils import utils_user_auth

async def logout_view(request: HttpRequest):
    """
    Deelte the cookies of auth to ensure logout
    """
    if request.method == 'GET':
        csrf_token = request.COOKIES.get('csrftoken')
        response = render(request,"logout.html", {"csrftoken": csrf_token})
        response["X-Page-Name"] = "logout.html"
        return response

    print("\n\n\nLOUGOUT VIEW CALLLLED\n\n\n", flush=True)
    if request.method == 'POST':
        response = await utils_user_auth.logout_handler()
        return response

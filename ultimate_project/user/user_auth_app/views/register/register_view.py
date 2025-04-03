from django.shortcuts import render
import json
import os
from itsdangerous import URLSafeTimedSerializer
# from django.http import HttpResponseBadRequest
from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache
from utils import utils_user_auth

from utils import utils_user_auth

async def register_view(request: HttpRequest):
    
    if request.method == 'GET':
        csrf_token = request.COOKIES.get('csrftoken')
        response = render(request,"register.html", {"csrftoken": csrf_token})
        response["X-Page-Name"] = "register.html"
        return response
    
    if request.method == 'POST':
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        # Create a new response object
        return await utils_user_auth.register_api(username, password, 
                        email, first_name, last_name)

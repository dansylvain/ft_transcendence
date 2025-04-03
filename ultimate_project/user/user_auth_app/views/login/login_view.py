# from django.views.decorators.http import require_POST
from django.shortcuts import render
import json
import os
from itsdangerous import URLSafeTimedSerializer
# from django.http import HttpResponseBadRequest
from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache
from utils import utils_user_auth

@never_cache
async def login_view(request: HttpRequest):
    """
    Extracts form data and passes it to `login_fastAPI`
    """
    print("\n===========\nLOGIN VIEW CALLED\n===========\n", flush=True)
    if request.method == 'GET':
        csrf_token = request.COOKIES.get('csrftoken')
        response = render(request,"login.html", {"csrftoken": csrf_token})
        response["X-Page-Name"] = "login.html"
        return response
        
    if request.method == 'POST':
        username = request.POST.get("username")  # Get username from POST data
        password = request.POST.get("password")  # Get password from POST data
        # Handle case if username or password is missing
        """ if not username or not password:
            return HttpResponseForbidden("Username or password missing") """
        response = await utils_user_auth.login_handler(username, password) 
        return (response)    


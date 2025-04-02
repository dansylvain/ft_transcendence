# from django.views.decorators.http import require_POST
from django.shortcuts import render
import json
import os
from itsdangerous import URLSafeTimedSerializer
# from django.http import HttpResponseBadRequest
from django.http import HttpRequest, JsonResponse

from utils import utils_user_auth

async def login_view(request: HttpRequest):
    """
    Extracts form data and passes it to `login_fastAPI`
    """
    print("\n===========\nLOGIN VIEW CALLED\n===========\n", flush=True)
    if request.method == 'GET':
        csrf_token = request.COOKIES.get('csrftoken')
        print(f"\n == CSRF TOKEN PRINT: {csrf_token} == \n", flush=True)
        response = render(request, "login.html", {"csrftoken": csrf_token})
        return response
        
    if request.method == 'POST':
        username = request.POST.get("username")  # Get username from POST data
        password = request.POST.get("password")  # Get password from POST data
        # Handle case if username or password is missing
        """ if not username or not password:
            return HttpResponseForbidden("Username or password missing") """
        response = await utils_user_auth.login_handler(username, password)        
        print(f"\n === \n RESPONSE DJANGO:\n n {response.content.decode('utf-8')}", flush=True)
        print(f"\n === \n RESPONSE DJANGO HEADERS:\n {response.headers}", flush=True)
        print(f"\n === \n RESPONSE DJANGO COOKIES:\n {response.cookies}", flush=True)
        return (response)    


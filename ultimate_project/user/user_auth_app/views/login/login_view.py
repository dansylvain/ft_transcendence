# from django.views.decorators.http import require_POST
from django.shortcuts import render
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
        print("\n===========\nLOGIN VIEW RECEIVED THE GET\n===========\n", flush=True)
        # i ened to do an api requets to check if a user is alredy
        csrf_token = request.COOKIES.get('csrftoken')
        print(f"\n == CSRF TOKEN PRINT: {csrf_token} == \n", flush=True)
        response = render(request, "login.html", {"csrftoken": csrf_token})
        #response.set_cookie('csrf_token', csrf_token)
        return response
        
    if request.method == 'POST':
        username = request.POST.get("username")  # Get username from POST data
        password = request.POST.get("password")  # Get password from POST data
        # Handle case if username or password is missing
        """ if not username or not password:
            return HttpResponseForbidden("Username or password missing") """
        response = await utils_user_auth.login_api(username, password)
        # Now you can call the login logic with username and password
        return response
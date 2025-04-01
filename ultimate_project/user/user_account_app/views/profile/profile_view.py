import os
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from utils import manage_user_data

async def profile_view(request: HttpRequest):
    # Get username from the JWT header
    
    print("PROFILE VIEW CALLED\n", flush=True) #rm

    username = request.headers.get("X-Username")
    
    print(f"username: {username}\n", flush=True)

    context = {
        "rasp": os.getenv("rasp", "false"),
        "pidom": os.getenv("pi_domain", "localhost:8443"),
    }
    
    if username:
        user = await manage_user_data.get_user_info_w_username(username)
        if user:
            context["user"] = user

    #if htmx request with inner content no need to resent the account html 
    if request.headers.get("HX-Request"):
        if request.headers.get("X-Inner-Content") == "true":
            return render(request, "partials/profile/profile.html", context)

    # If it's a full page loading
    return render(request, "layouts/account.html", {
        "username": username,
        "page": "partials/profile/profile.html",
        **context
    })

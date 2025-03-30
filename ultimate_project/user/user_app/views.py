import os
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.http import HttpRequest
from django.template.loader import render_to_string
import httpx


async def get_user_info(username):
    """
    Get user information by username from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            print("\nCALLLED GET USER INFO\n", flush=True) # rm
            
            response = await client.get(
                f"http://ctn_api_gateway:8005/api/player/?username={username}"
            )

            
            response_text = response.text  # For plain text responses
            print("\n API USER response: ", response_text, "\n", flush=True) #rm

            if response.status_code == 200:
                data = response.json()
                # Check if response is a list (direct array)
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                # Check if response has 'results' field (paginated)
                elif (
                    isinstance(data, dict)
                    and data.get("results")
                    and len(data["results"]) > 0
                ):
                    return data["results"][0]

            return None
    except Exception as e:
        print(f"Error getting user by username: {str(e)}", flush=True)
        return None


async def profile(request: HttpRequest):
    # Get username from the JWT header
    
    print("PROFILE TMP CALLED\n", flush=True) #rm

    username = request.headers.get("X-Username")
    
    print(f"username: {username}\n", flush=True)

    context = {
        "rasp": os.getenv("rasp", "false"),
        "pidom": os.getenv("pi_domain", "localhost:8443"),
    }

    print("PROFILE TMP CALLED\n", flush=True) #rm
    
    if username:
        user = await get_user_info(username)
        if user:
            context["user"] = user

    #if htmx request with inner content no need to resent the account html 
    if request.headers.get("HX-Request"):
        if request.headers.get("X-Inner-Content") == "true":
            return render(request, "partials/profile.html", context)

    # If it's a full page loading
    return render(request, "account.html", 
                  {**context, "page": "partials/profile.html"})  

#no useful
#@cache_control(no_cache=True, must_revalidate=True)
async def game_stats(request: HttpRequest):
    
    username = request.headers.get("X-Username")

    context = {
        "rasp": os.getenv("rasp", "false"),
        "pidom": os.getenv("pi_domain", "localhost:8443"),
    }

    if username:
        user = await get_user_info(username)
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
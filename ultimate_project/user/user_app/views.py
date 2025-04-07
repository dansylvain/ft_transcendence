import os
from django.shortcuts import render
from django.http import HttpRequest
import httpx


async def get_user_by_username(username):
    """
    Get user information by username from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://databaseapi:8007/api/player/?username={username}"
            )

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
    username = request.headers.get("X-Username")

    context = {
        "rasp": os.getenv("rasp", "false"),
        "pidom": os.getenv("HOST_IP", "localhost:8443"),
    }

    if username:
        user = await get_user_by_username(username)
        if user:
            context["user"] = user

    return render(
        request,
        "profile.html",
        context,
    )


def stats(request: HttpRequest):
    return render(
        request,
        "stats.html",
        {
            "rasp": os.getenv("rasp", "false"),
            "pidom": os.getenv("HOST_IP", "localhost:8443"),
        },
    )

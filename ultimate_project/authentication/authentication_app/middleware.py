import json
import requests
from django.http import JsonResponse
from django.urls import resolve


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that don't require authentication
        self.public_paths = [
            "/login/",
            "/register/",
            "/refresh-token/",
            "/health/",  # For health checks
            "/static/",  # For static files
        ]

    def __call__(self, request):
        # Get the current path
        current_path = request.path_info

        # Check if the path is public
        if any(current_path.startswith(path) for path in self.public_paths):
            return self.get_response(request)

        # Get the access token from cookies
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            # No token, redirect to login
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                # AJAX request
                return JsonResponse({"error": "Authentication required"}, status=401)
            else:
                # Regular request
                from django.shortcuts import redirect

                return redirect("login")

        # Verify the token with the database API
        try:
            # Add the token to the request for downstream use
            request.access_token = access_token

            # Continue with the request
            response = self.get_response(request)

            return response
        except Exception as e:
            # Token verification failed
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                # AJAX request
                return JsonResponse({"error": str(e)}, status=401)
            else:
                # Regular request
                from django.shortcuts import redirect

                return redirect("login")

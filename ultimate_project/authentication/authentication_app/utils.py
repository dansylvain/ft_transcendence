import requests
from django.conf import settings
from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect


def verify_jwt_token(token):
    """
    Verify a JWT token by making a request to the database API.
    Returns the decoded token payload if valid, None otherwise.
    """
    try:
        # Make a request to the database API to verify the token
        response = requests.post(
            "http://databaseapi:8007/api/token/verify/", data={"token": token}
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def jwt_required(view_func):
    """
    Decorator to require a valid JWT token for a view.
    If the token is invalid, redirects to the login page.
    """

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Get the token from cookies
        token = request.COOKIES.get("access_token")

        if not token:
            # No token, redirect to login
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                # AJAX request
                return JsonResponse({"error": "Authentication required"}, status=401)
            else:
                # Regular request
                return redirect(settings.LOGIN_URL)

        # Verify the token
        payload = verify_jwt_token(token)

        if not payload:
            # Invalid token, redirect to login
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                # AJAX request
                return JsonResponse({"error": "Invalid token"}, status=401)
            else:
                # Regular request
                return redirect(settings.LOGIN_URL)

        # Add the payload to the request
        request.jwt_payload = payload

        # Continue with the view
        return view_func(request, *args, **kwargs)

    return wrapped_view


def get_user_from_token(token):
    """
    Get user information from a JWT token.
    Returns the user data if valid, None otherwise.
    """
    try:
        # Make a request to the database API to get user info from the token
        response = requests.get(
            "http://databaseapi:8007/api/user-from-token/",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

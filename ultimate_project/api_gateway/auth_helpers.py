import jwt, os
from fastapi import Request
from fastapi.responses import RedirectResponse

JWT_SECRET_KEY = os.getenv("JWT_KEY")


def block_authenticated_users():
    """
    Dependency function that prevents authenticated users from accessing certain routes.
    Redirects authenticated users to /home/

    Returns:
        - RedirectResponse to /home/ if user is authenticated
        - None if user is not authenticated (allowing the route handler to continue)
    """

    async def dependency(request: Request):
        access_token = request.cookies.get("access_token")

        if access_token:
            try:
                # Try to decode the token
                payload = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=["HS256"])
                # If successful, user is authenticated - redirect to home
                print("⛔ USER IS AUTHENTICATED - REDIRECTING TO HOME ⛔", flush=True)
                return RedirectResponse(url="/home/")
            except jwt.ExpiredSignatureError:
                print("✅ ACCESS TOKEN EXPIRED - ALLOWING LOGIN ✅", flush=True)
                pass  # Token expired, allow access
            except jwt.InvalidTokenError:
                print("✅ INVALID ACCESS TOKEN - ALLOWING LOGIN ✅", flush=True)
                pass  # Invalid token, allow access

        # Not authenticated, allow access
        return None

    return dependency

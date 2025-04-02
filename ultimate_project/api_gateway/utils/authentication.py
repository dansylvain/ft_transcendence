# from django.middleware.csrf import get_token
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import requests
import jwt
import datetime
import os
import pyotp
import re
import secrets
import hashlib


# Clé secrète pour signer les JWT
SECRET_JWT_KEY = os.getenv("JWT_KEY")

# Configuration des durées des tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# URL de l'API qui gère la vérification des identifiants
DATABASE_API_URL = "http://databaseapi:8007/api-database/verify-credentials/"
CHECK_2FA_URL = "http://databaseapi:8007/api-database/check-2fa/"


def generate_django_csrf_token():
    secret = secrets.token_hex(32)  # 32-byte secret key
    hashed_token = hashlib.sha256(secret.encode()).hexdigest()
    return hashed_token


# Function to verify JWT token
def verify_jwt(token):
    """
    Verify a JWT token and return the payload if valid.

    Args:
        token (str): The JWT token to verify

    Returns:
        dict: The decoded token payload if valid, None otherwise
    """
    try:
        # Verify the token with our secret key
        payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


# Function to generate a new access token using a valid refresh token
def generate_access_token_from_refresh_token(refresh_payload):
    """
    Generate a new access token from a valid refresh token payload.
    Args:
        refresh_payload (dict): The decoded refresh token payload
    Returns:
        str: The newly generated access token
    """
    # Create a new access token with the same user info
    user_id = refresh_payload.get("user_id")
    username = refresh_payload.get("username")  # Extract username from refresh token
    # Set expiration for new access token
    expire_access = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # Create payload for new access token
    access_payload = {
        "user_id": user_id,
        "username": username,  # Include username in new access token
        "exp": expire_access,
    }
    # Generate and return the new access token
    new_access_token = jwt.encode(access_payload, SECRET_JWT_KEY, algorithm="HS256")
    print(f"🔄 Generated new access token: {new_access_token[:20]}...", flush=True)

    return new_access_token


# Function to check if a user is authenticated based on cookies
def is_authenticated(request: Request):
    """
    Check if the request contains valid authentication cookies.

    Args:
        request (Request): The FastAPI request object

    Returns:
        tuple: (is_authenticated, user_info)
    """
    # Get the access token from cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        return False, None

    # Verify the token
    payload = verify_jwt(access_token)
    if not payload:
        # If access token is invalid, check refresh token
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return False, None

        refresh_payload = verify_jwt(refresh_token)
        if not refresh_payload:
            return False, None

        # Implement token refresh
        new_access_token = generate_access_token_from_refresh_token(refresh_payload)

        # Set new access token in the response
        # Since this is middleware and not a full response handler,
        # we'll need to return a signal to set a new cookie
        return True, {
            "user_id": refresh_payload.get("user_id"),
            "username": refresh_payload.get(
                "username"
            ),  # Include username from refresh token
            "refresh_needed": True,
            "new_access_token": new_access_token,
        }

    # Return authentication status and user info from the valid access token
    return True, {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
    }


# Function to verify 2FA code and generate JWT tokens
async def verify_2fa_and_login(
    request: Request,
    response: Response,
    username: str,
    token: str,
):
    """
    Verifies 2FA code and generates JWT tokens if valid.

    Args:
        request (Request): The FastAPI request object
        response (Response): The FastAPI response object
        username (str): The username
        token (str): The 2FA verification code

    Returns:
        JSONResponse with JWT tokens if 2FA code is valid
    """
    print(f"🔐 Verifying 2FA for {username}, token: {token}", flush=True)
    print(f"🔐 Request form data: {await request.form()}", flush=True)
    print(f"🔐 Request headers: {request.headers}", flush=True)

    if not username or not token:
        print("❌ Username or token missing", flush=True)
        if not username:
            print("❌ Username is missing", flush=True)
        if not token:
            print("❌ Token is missing", flush=True)

        # Try to get username from form directly as fallback
        if not username:
            form_data = await request.form()
            username = form_data.get("username")
            print(f"🔑 Extracted username from form: {username}", flush=True)

        if not token:
            form_data = await request.form()
            token = form_data.get("token")
            print(f"🔑 Extracted token from form: {token}", flush=True)

        # If still missing after fallback, return error
        if not username or not token:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Username and token are required",
                },
                status_code=400,
            )

    # Call the database API to verify the 2FA code
    try:
        # Get user data first to retrieve the secret
        get_user_url = f"http://databaseapi:8007/api-database/player/?username={username}"
        print(f"🔍 Querying database API for user: {get_user_url}", flush=True)
        user_response = requests.get(get_user_url)

        if user_response.status_code != 200:
            print(
                f"❌ Failed to retrieve user information: {user_response.status_code}",
                flush=True,
            )
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Failed to retrieve user information",
                },
                status_code=500,
            )

        user_data = user_response.json()
        print(f"🔍 User data response: {user_data}", flush=True)

        # Check if we got a list of users or a paginated response
        if isinstance(user_data, list) and len(user_data) > 0:
            user = user_data[0]
            print(f"✅ Found user in list format", flush=True)
        elif (
            isinstance(user_data, dict)
            and user_data.get("results")
            and len(user_data["results"]) > 0
        ):
            user = user_data["results"][0]
            print(f"✅ Found user in paginated response", flush=True)
        else:
            print(f"❌ User not found in response", flush=True)
            return JSONResponse(
                content={"success": False, "message": "User not found"}, status_code=404
            )

        print(f"🔍 User object: {user}", flush=True)

        # Verify the 2FA token
        secret = user.get("_two_fa_secret")
        if not secret:
            print(f"❌ 2FA secret not found for user", flush=True)
            return JSONResponse(
                content={"success": False, "message": "2FA not set up properly"},
                status_code=400,
            )

        print(f"🔑 Using secret to verify token", flush=True)
        totp = pyotp.TOTP(secret)
        if not totp.verify(token):
            print(f"❌ Invalid 2FA code", flush=True)
            return JSONResponse(
                content={"success": False, "message": "Invalid 2FA code"},
                status_code=401,
            )

        print(f"✅ 2FA code verified successfully", flush=True)

        # 2FA verification succeeded, generate JWT tokens
        user_id = user.get("id")

        # Generate JWT tokens
        expire_access = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        expire_refresh = datetime.datetime.utcnow() + datetime.timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )

        access_payload = {
            "user_id": user_id,
            "username": username,
            "exp": expire_access,
        }
        refresh_payload = {
            "user_id": user_id,
            "username": username,
            "exp": expire_refresh,
        }

        access_token = jwt.encode(access_payload, SECRET_JWT_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, SECRET_JWT_KEY, algorithm="HS256")

        # Log for debug
        print(f"2FA Verified. Access Token: {access_token[:20]}...", flush=True)
        print(f"2FA Verified. Refresh Token: {refresh_token[:20]}...", flush=True)

        # Create a JSONResponse with success message
        json_response = JSONResponse(
            content={"success": True, "message": "2FA verification successful"}
        )

        # Set cookies on the response
        json_response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 6,  # 6 hours
        )

        json_response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 24 * 7,  # 7 days
        )

        # Generate and set CSRF token
        #csrf_token = secrets.token_urlsafe(64)
        json_response.set_cookie(
            key="csrftoken",
            value=generate_django_csrf_token(),
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 6,  # 6 hours, same as access token
        )

        # Debug log for headers
        print(f"🔒 Response headers: {dict(json_response.headers)}", flush=True)

        return json_response

    except requests.exceptions.RequestException as e:
        return JSONResponse(
            content={"success": False, "message": f"Service unavailable: {str(e)}"},
            status_code=500,
        )
    except Exception as e:
        print(f"Error in verify_2fa_and_login: {str(e)}", flush=True)
        return JSONResponse(
            content={
                "success": False,
                "message": f"Error processing request: {str(e)}",
            },
            status_code=500,
        )


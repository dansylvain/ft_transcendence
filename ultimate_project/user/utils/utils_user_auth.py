# from django.middleware.csrf import get_token
import jwt, os
from django.http import JsonResponse
from django.http import HttpRequest
import requests
import datetime
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

API_VERIFY_CREDENTIALS = "http://ctn_api_gateway:8005/api/verify-credentials/"
API_CHECK_2FA = "http://ctn_api_gateway:8005/api/check-2fa/"


def generate_django_csrf_token():
    secret = secrets.token_hex(32)  # 32-byte secret key
    hashed_token = hashlib.sha256(secret.encode()).hexdigest()
    return (hashed_token)

async def login_api(username: str, password: str):
    """
    Vérifie les identifiants via `databaseAPI`, puis génère un JWT stocké en cookie.
    """
    
    print(f"🔐 Tentative de connexion pour {username}", flush=True)

    # Vérifier les identifiants en appelant `databaseAPI`
    try:
        #do
        db_response = requests.post(
            API_VERIFY_CREDENTIALS,
            data={"username": username, "password": password},
        )

        if db_response.status_code != 200:
            error_message = db_response.json().get("error", "Authentication failed")
            # Return error message to be displayed in the login-result div
            return JsonResponse(
                content={"success": False, "message": error_message}, status_code=401
            )

        # 🔹 L'authentification est réussie, récupérer les données utilisateur
        auth_data = db_response.json()

    except requests.exceptions.RequestException as e:
        # Return error message for connection issues
        return JsonResponse(
            content={"success": False, "message": f"Service unavailable: {str(e)}"},
            status_code=500,
        )

    # Check if 2FA is enabled
    check_2fa_response = requests.post(
        API_CHECK_2FA, data={"username": username, "password": password}
    )

    # If 2FA is enabled, return 2FA connection page
    if check_2fa_response.status_code == 200:
        return JsonResponse(
            content={"success": False, "message": "2FA is enabled"}, status_code=401
        )

    # 🔹 Générer les tokens JWT
    expire_access = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    expire_refresh = datetime.datetime.utcnow() + datetime.timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    access_payload = {
        "user_id": auth_data.get("user_id", 0),
        "username": username,
        "exp": expire_access,
    }
    refresh_payload = {
        "user_id": auth_data.get("user_id", 0),
        "username": username,  # Include username in refresh token too
        "exp": expire_refresh,
    }

    access_token = jwt.encode(access_payload, SECRET_JWT_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, SECRET_JWT_KEY, algorithm="HS256")

    # 🔹 Log pour debug
    print(f"Access Token: {access_token[:20]}...", flush=True)
    print(f"Refresh Token: {refresh_token[:20]}...", flush=True)

    # 🔹 Indiquer à HTMX de rediriger l'utilisateur
    # response.headers["HX-Redirect"] = "/home"
    # response.headers["HX-Login-Success"] = "true"

    # Create a JSONResponse with success message
    json_response = JsonResponse(
        content={"success": True, "message": "Connexion réussie"}
    )

    # Copy the headers from our response to the JSONResponse
    # for key, value in response.headers.items():
    #     json_response.headers[key] = value

    # Make sure the cookies are also set on the JSONResponse
    # Access token
    json_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        path="/",
        max_age=60 * 60 * 6,
    )

    # Refresh token
    json_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        path="/",
        max_age=60 * 60 * 24 * 7,
    )

    # Generate and set CSRF token
    # csrf_token = secrets.token_urlsafe(64)
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

# Function to handle user logout
async def logout_api():
    
    print("🚪 Logout requested", flush=True)

    # Create response
    response = JsonResponse(content={"success": True, "message": "Déconnexion réussie"})

    # Clear cookies by setting them with empty values and making them expire immediately
    response.delete_cookie(
        key="access_token",
        path="/",  # Must match how it was set
        httponly=True,  # Must match how it was set
        samesite="Lax",  # Must match how it was set
    )

    response.delete_cookie(
        key="refresh_token",
        path="/",  # Must match how it was set
        httponly=True,  # Must match how it was set
        samesite="Lax",  # Must match how it was set
    )

    # Add a header for HTMX to redirect to login page
    # response.headers["HX-Redirect"] = "/login"
    # Log for debugging
    print("🔑 JWT Cookies cleared", flush=True)

    return (response)

async def register_api(
    username: str,
    password: str,
    email: str,
    first_name: str,
    last_name: str,
):
    """
    Register a new user and return a JWT token.
    """
    print(f"🔐 Tentative d'inscription pour {username}", flush=True)

    # Regex patterns for input validation
    name_pattern = r"^(?!.*--)[a-zA-ZÀ-ÿ0-9\-]+$"
    # == Validate first name == 
    if not re.match(name_pattern, first_name):
        return JsonResponse(
            content={
                "success": False,
                "message": "Forbidden characters in first name. Allowed characters: a-z, A-Z, 0-9, -, _",
            },
            status_code=400,
        )
    # == Validate last name == 
    if not re.match(name_pattern, last_name):
        return JsonResponse(
            content={
                "success": False,
                "message": "Forbidden characters in last name. Allowed characters: a-z, A-Z, 0-9, -, _",
            },
            status_code=400,
        )
    username_pattern = r"^(?!.*--)[a-zA-Z0-9_\-]+$"
    # == Validate username == 
    if not re.match(username_pattern, username):
        return JsonResponse(
            content={
                "success": False,
                "message": "Forbidden characters in username. Allowed characters: a-z, A-Z, 0-9, -, _",
            },
            status_code=400,
        )
    password_pattern = r"^(?!.*--)[a-zA-Z0-9_\-?!$€%&*()]+$"
    # == Validate password == 
    if not re.match(password_pattern, password):
        return JsonResponse(
            content={
                "success": False,
                "message": "Forbidden characters in password. Allowed characters: a-z, A-Z, 0-9, -, _, !, ?, $, €, %, &, *, (, )",
            },
            status_code=400,
        )

    # Check if username already exists first (industry standard to check one field at a time)
    try:
        # == Query for existing users with this username == 
        # MODIFY WITH CALL TO FAST API
        check_username_url = "http://ctn_api_gateway:8005/api/player/?username=" + username
        username_response = requests.get(check_username_url)

        if username_response.status_code == 200:
            user_data = username_response.json()
            # Handle case where user_data is a list (checking if username exists)
            if isinstance(user_data, list) and len(user_data) > 0:
                return JsonResponse(
                    content={
                        "success": False,
                        "message": "Username already taken.",
                    },
                    status_code=400,
                )
            # Handle case where user_data is a dict with count key
            elif isinstance(user_data, dict) and user_data.get("count", 0) > 0:
                return JsonResponse(
                    content={
                        "success": False,
                        "message": "Username already taken.",
                    },
                    status_code=400,
                )

        # == Then check if email already exists == 
        check_email_url = "http://ctn_api_gateway:8005/api/player/?email=" + email
        email_response = requests.get(check_email_url)

        if email_response.status_code == 200:
            email_data = email_response.json()
            # Handle case where email_data is a list
            if isinstance(email_data, list) and len(email_data) > 0:
                return JsonResponse(
                    content={
                        "success": False,
                        "message": "Email adress already taken.",
                    },
                    status_code=400,
                )
            # Handle case where email_data is a dict with count key
            elif isinstance(email_data, dict) and email_data.get("count", 0) > 0:
                return JsonResponse(
                    content={
                        "success": False,
                        "message": "Email adress already taken.",
                    },
                    status_code=400,
                )

        # == If no duplicates, create the new user == 
        create_user_url = "http://ctn_api_gateway:8005/api/player/"
        registration_data = {
            "username": username,
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        }

        # Debug info
        print(f"📝 Sending registration data: {registration_data}", flush=True)

        create_response = requests.post(
            create_user_url,
            json=registration_data,
            headers={"Content-Type": "application/json"},  # Ensure correct content type
        )

        # == Check if user creation was successful == 
        if create_response.status_code not in (200, 201):
            error_message = create_response.json().get("error", "Registration failed")
            return JsonResponse(
                content={"success": False, "message": error_message},
                status_code=create_response.status_code,
            )

        # == User was created successfully, get user data for JWT == 
        user_data = create_response.json()

        # Generate JWT tokens like in login
        expire_access = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        expire_refresh = datetime.datetime.utcnow() + datetime.timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )

        # == Create payloads for tokens ==
        access_payload = {
            "user_id": user_data.get("id", 0),
            "username": username,
            "exp": expire_access,
        }
        refresh_payload = {
            "user_id": user_data.get("id", 0),
            "username": username,
            "exp": expire_refresh,
        }

        # == Generate tokens == 
        access_token = jwt.encode(access_payload, SECRET_JWT_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, SECRET_JWT_KEY, algorithm="HS256")

        # Debug logging
        print(f"Registration successful for {username}", flush=True)
        print(f"Access Token: {access_token}...", flush=True)
        print(f"Refresh Token: {refresh_token}...", flush=True)

        # Set redirect header for HTMX
        # response.headers["HX-Redirect"] = "/home"

        # == Create the response object == 
        json_response = JsonResponse(
            content={"success": True, "message": "Inscription réussie"}
        )

        # Copy headers from our response to the JSONResponse
        # for key, value in response.headers.items():
        #     json_response.headers[key] = value

        # == Set JWT cookies == 
        # == Set access token ==
        json_response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 6,  # 6 hours
        )
        # == Set refresh token ==
        json_response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 24 * 7,  # 7 days
        )

        # == Generate and set CSRF token == 
        # csrf_token = secrets.token_urlsafe(64)
        json_response.set_cookie(
            key="csrftoken",
            value=generate_django_csrf_token(),
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 6,  # 6 hours, same as access token
        )

        return json_response

    except requests.exceptions.RequestException as e:
        # Handle any network or connection errors
        return JsonResponse(
            content={"success": False, "message": f"Service unavailable: {str(e)}"},
            status_code=500,
        )


# Function to verify 2FA code and generate JWT tokens
async def verify_2fa_and_login(
    request: HttpRequest,
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
            return JsonResponse(
                content={
                    "success": False,
                    "message": "Username and token are required",
                },
                status_code=400,
            )

    # Call the database API to verify the 2FA code
    try:
        # Get user data first to retrieve the secret
        get_user_url = f"http://databaseapi:8007/api/player/?username={username}"
        print(f"🔍 Querying database API for user: {get_user_url}", flush=True)
        user_response = requests.get(get_user_url)

        if user_response.status_code != 200:
            print(
                f"❌ Failed to retrieve user information: {user_response.status_code}",
                flush=True,
            )
            return JsonResponse(
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
            return JsonResponse(
                content={"success": False, "message": "User not found"}, status_code=404
            )

        print(f"🔍 User object: {user}", flush=True)

        # Verify the 2FA token
        secret = user.get("_two_fa_secret")
        if not secret:
            print(f"❌ 2FA secret not found for user", flush=True)
            return JsonResponse(
                content={"success": False, "message": "2FA not set up properly"},
                status_code=400,
            )

        print(f"🔑 Using secret to verify token", flush=True)
        totp = pyotp.TOTP(secret)
        if not totp.verify(token):
            print(f"❌ Invalid 2FA code", flush=True)
            return JsonResponse(
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
        json_response = JsonResponse(
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
        # csrf_token = secrets.token_urlsafe(64)
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
        return JsonResponse(
            content={"success": False, "message": f"Service unavailable: {str(e)}"},
            status_code=500,
        )
    except Exception as e:
        print(f"Error in verify_2fa_and_login: {str(e)}", flush=True)
        return JsonResponse(
            content={
                "success": False,
                "message": f"Error processing request: {str(e)}",
            },
            status_code=500,
        )


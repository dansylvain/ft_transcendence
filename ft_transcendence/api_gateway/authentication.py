from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
import requests
import jwt
import datetime
import os
import pyotp
import re
import uuid

# Custom Imports
from generate_cookies import generate_cookies
from auth_utils import update_uuid, delete_uuid

router = APIRouter()

SECRET_JWT_KEY = os.getenv("JWT_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = 120
REFRESH_TOKEN_EXPIRE_DAYS = 5

# API urls for checking users IDs
DATABASE_API_URL = "http://databaseapi:8007/api/verify-credentials/"
CHECK_2FA_URL = "http://databaseapi:8007/api/check-2fa/"


async def login_fastAPI(
    request: Request,
    response: Response,
    username: str,
    password: str,
):

    print(f"🔐 User {username} tries to connect...", flush=True)

    # Calls `databaseAPI` container for checking ID
    try:
        db_response = requests.post(
            DATABASE_API_URL,
            data={"username": username, "password": password},
        )

        if db_response.status_code != 200:
            error_message = db_response.json().get("error", "Authentication failed")
            # Return error message to be displayed in the login-result div
            return JSONResponse(
                content={"success": False, "message": error_message}, status_code=401
            )

        auth_data = db_response.json()

    except requests.exceptions.RequestException as e:
        return JSONResponse(
            content={"success": False, "message": f"Service unavailable: {str(e)}"},
            status_code=500,
        )

    # Check if 2FA is enabled
    check_2fa_response = requests.post(
        CHECK_2FA_URL, data={"username": username, "password": password}
    )

    # If 2FA is enabled, return 2FA connection page
    if check_2fa_response.status_code == 200:
        return JSONResponse(
            content={"success": False, "message": "2FA is enabled"}, status_code=200
        )

    # Generates expiration dates for JWT
    expire_access = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_refresh = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    my_uuid = str(uuid.uuid4())
    user_id = auth_data.get("user_id", 0)

    # Store the UUID in the database, for preventing double login behaviour
    update_uuid(my_uuid, user_id, "regular login")

    access_payload = {
        "user_id": user_id,
        "username": username,
        "uuid": my_uuid,  # ! IMPORTANT Include UUID in the payload ...
        "exp": expire_access,
    }
    refresh_payload = {
        "user_id": user_id,
        "username": username,
        "uuid": my_uuid,  #!... and in the refresh token for avoid generating a double UUID for double auth process
        "exp": expire_refresh,
    }

    # Encode the payloads in JWT tokens
    access_token = jwt.encode(access_payload, SECRET_JWT_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, SECRET_JWT_KEY, algorithm="HS256")

    json_response = JSONResponse(
        content={"success": True, "message": "Connexion réussie"}
    )

    generate_cookies(json_response, access_token, refresh_token)

    print(f"🔒 Response headers: {dict(json_response.headers)}", flush=True)

    return json_response


async def logout_fastAPI(request: Request):

    print("🚪 Logout requested", flush=True)

    # Get user ID from the token to clear the session
    access_token = request.cookies.get("access_token")

    if access_token:
        delete_uuid(access_token)

    response = JSONResponse(content={"success": True, "message": "Déconnexion réussie"})

    # Clear JWT + CSRF cookies
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="Lax",
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        samesite="Lax",
    )
    response.delete_cookie(
        key="csrftoken",
        path="/",
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    # print("🔑 JWT Cookies cleared", flush=True)
    return response


# Function to verify 2FA code and generate JWT tokens
async def verify_2fa_and_login(
    request: Request,
    response: Response,
    username: str,
    token: str,
):

    print(f"🔐 Verifying 2FA for {username}, otp: {token}", flush=True)

    # Try to get username from form directly as fallback
    if not username or not token:
        
        # Extract form data once instead of twice
        form_data = await request.form()

        if not username:
            username = form_data.get("username")

        if not token:
            token = form_data.get("token")

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
        get_user_url = f"http://databaseapi:8007/api/player/?username={username}"
        user_response = requests.get(get_user_url)

        if user_response.status_code != 200:
            
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Failed to retrieve user information",
                },
                status_code=500,
            )

        user_data = user_response.json()

        # Check if we got a list of users or a paginated response
        if isinstance(user_data, list) and len(user_data) > 0:
            user = user_data[0]
        elif (
            isinstance(user_data, dict)
            and user_data.get("results")
            and len(user_data["results"]) > 0
        ):
            user = user_data["results"][0]
        else:
            print(f"❌ User not found in response", flush=True)
            return JSONResponse(
                content={"success": False, "message": "User not found"}, status_code=404
            )

        # Verify the 2FA token
        secret = user.get("_two_fa_secret")
        if not secret:
            return JSONResponse(
                content={"success": False, "message": "2FA not set up properly"},
                status_code=400,
            )

        totp = pyotp.TOTP(secret)
        if not totp.verify(token):
            return JSONResponse(
                content={"success": False, "message": "Invalid 2FA code"},
                status_code=401,
            )

        print(f"✅ 2FA code verified successfully", flush=True)

        # ! At this point : 2FA verification succeeded ==> generate JWT tokens
        user_id = user.get("id")

        # Generate JWT tokens
        expire_access = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire_refresh = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Generate a unique session ID
        my_uuid = str(uuid.uuid4())

        update_uuid(my_uuid, user_id, "2FA Login")

        access_payload = {
            "user_id": user_id,
            "username": username,
            "uuid": my_uuid,
            "exp": expire_access,
        }
        refresh_payload = {
            "user_id": user_id,
            "username": username,
            "uuid": my_uuid,
            "exp": expire_refresh,
        }

        access_token = jwt.encode(access_payload, SECRET_JWT_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, SECRET_JWT_KEY, algorithm="HS256")

        # Create a JSONResponse with success message
        json_response = JSONResponse(
            content={"success": True, "message": "2FA verification successful"}
        )

        generate_cookies(json_response, access_token, refresh_token)

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


async def register_fastAPI(
    request: Request,
    response: Response,
    username: str,
    password: str,
    email: str,
    first_name: str,
    last_name: str,
):
    print(f"🔐 Registering attempt for {username}", flush=True)

    # Regex patterns for input validation
    name_pattern = r"^(?!.*--)[a-zA-ZÀ-ÿ0-9\-]+$"

    # Validate first name
    if not re.match(name_pattern, first_name):
        return JSONResponse(
            content={
                "success": False,
                "message": "Forbidden characters in first name. Allowed characters: a-z, A-Z, 0-9, -, _",
            },
            status_code=400,
        )

    # Validate last name
    if not re.match(name_pattern, last_name):
        return JSONResponse(
            content={
                "success": False,
                "message": "Forbidden characters in last name. Allowed characters: a-z, A-Z, 0-9, -, _",
            },
            status_code=400,
        )

    username_pattern = r"^(?!.*--)[a-zA-Z0-9_\-]+$"
    # Validate username
    if not re.match(username_pattern, username):
        return JSONResponse(
            content={
                "success": False,
                "message": "Forbidden characters in username. Allowed characters: a-z, A-Z, 0-9, -, _",
            },
            status_code=400,
        )

    password_pattern = r"^(?!.*--)[a-zA-Z0-9_\-?!$€%&*()]+$"
    # Validate password
    if not re.match(password_pattern, password):
        return JSONResponse(
            content={
                "success": False,
                "message": "Forbidden characters in password. Allowed characters: a-z, A-Z, 0-9, -, _, !, ?, $, €, %, &, *, (, )",
            },
            status_code=400,
        )

    # ! From here, every function call to the DB can raise an exception
    try:
        # * STEP 1 : Query DB for checking duplicates username
        check_username_url = "http://databaseapi:8007/api/player/?username=" + username
        username_response = requests.get(check_username_url)

        if username_response.status_code == 200:
            user_data = username_response.json()

            # Handle case where user_data is a list (checking if username exists)
            if isinstance(user_data, list) and len(user_data) > 0:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Username already taken.",
                    },
                    status_code=400,
                )

            # Handle case where user_data is a dict with count key
            elif isinstance(user_data, dict) and user_data.get("count", 0) > 0:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Username already taken.",
                    },
                    status_code=400,
                )

        # * STEP 2 : Query DB for checking duplicates emails
        check_email_url = "http://databaseapi:8007/api/player/?email=" + email
        email_response = requests.get(check_email_url)

        if email_response.status_code == 200:
            email_data = email_response.json()
            # Handle case where email_data is a list
            if isinstance(email_data, list) and len(email_data) > 0:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Email adress already taken.",
                    },
                    status_code=400,
                )
            # Handle case where email_data is a dict with count key
            elif isinstance(email_data, dict) and email_data.get("count", 0) > 0:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Email adress already taken.",
                    },
                    status_code=400,
                )

        # If no duplicates, create the new user
        create_user_url = "http://databaseapi:8007/api/player/"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        }

        create_response = requests.post(
            create_user_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        # Check if user creation was successful
        if create_response.status_code not in (200, 201):
            error_message = create_response.json().get("error", "Registration failed")
            return JSONResponse(
                content={"success": False, "message": error_message},
                status_code=create_response.status_code,
            )

        # User was created successfully, get user data for JWT
        user_data = create_response.json()

        # Generate JWT tokens like in login
        expire_access = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire_refresh = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Generate and update the user's UUID
        my_uuid = str(uuid.uuid4())
        user_id = user_data.get("id", 0)
        update_uuid(my_uuid, user_id, "Register")

        # Create payloads for tokens
        access_payload = {
            "user_id": user_id,
            "username": username,
            "uuid": my_uuid,
            "exp": expire_access,
        }
        refresh_payload = {
            "user_id": user_id,
            "username": username,
            "uuid": my_uuid,
            "exp": expire_refresh,
        }

        # Generate JWT tokens
        access_token = jwt.encode(access_payload, SECRET_JWT_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, SECRET_JWT_KEY, algorithm="HS256")

        print(f"Registration successful for {username}", flush=True)

        # Create the response object
        json_response = JSONResponse(
            content={"success": True, "message": "Inscription réussie"}
        )

        generate_cookies(json_response, access_token, refresh_token)

        return json_response

    except requests.exceptions.RequestException as e:
        # Handle any network or connection errors
        return JSONResponse(
            content={"success": False, "message": f"Service unavailable: {str(e)}"},
            status_code=500,
        )

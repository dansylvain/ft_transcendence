from fastapi import Request
import os
import jwt
import datetime
import requests

SECRET_JWT_KEY = os.getenv("JWT_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # print(f"Expired JWT key", flush=True)
        return None
    except jwt.InvalidTokenError:
        # print(f" !!!!!!!!! INVALID JWT key", flush=True)
        return None


# Function to generate a new access token using a valid refresh token
def refresh_access_token(refresh_payload):
    
    # Create a new access token with the same user info
    user_id = refresh_payload.get("user_id")
    username = refresh_payload.get("username")  # Extract username from refresh token

    # Get the current UUID for this user
    try:
        response = requests.get(f"http://databaseapi:8007/api/player/{user_id}/uuid")
        uuid_value = None
        if response.status_code == 200:
            session_data = response.json()
            uuid_value = session_data.get("uuid")
    except Exception as e:
        print(f"⚠️ Error retrieving UUID during refresh: {str(e)}", flush=True)
        uuid_value = None

    # Set expiration for new access token
    expire_access = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create payload for new access token
    access_payload = {
        "user_id": user_id,
        "username": username,
        "uuid": uuid_value,
        "exp": expire_access,
    }

    # Generate and return the new access token
    new_access_token = jwt.encode(access_payload, SECRET_JWT_KEY, algorithm="HS256")

    return new_access_token


# Function to check if a user is authenticated based on cookies
def is_authenticated(request: Request):

    # Get the access token from cookies
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    # 
    if access_token:
        # Verify the token
        payload = verify_jwt(access_token)
        if not payload and not refresh_token: # * EDGE CASE : access_token might be invalid and missing `refresh_token`
            return False, None
        elif not payload and refresh_token: # * EDGE CASE 2 : Invalid `access_token` invalid raises a 500 error
            refresh_payload = verify_jwt(refresh_token)
            if not refresh_payload:
                return False, None
            else: # ! NEED REFRESH TOKEN
                new_access_token = refresh_access_token(refresh_payload)
                
                return True, {
                    "user_id": refresh_payload.get("user_id"),
                    "username": refresh_payload.get("username"),
                    "refresh_needed": True,
                    "new_access_token": new_access_token,
                }
    elif refresh_token:
        refresh_payload = verify_jwt(refresh_token)
        if not refresh_payload:
            return False, None
        else: # ! NEED REFRESH TOKEN
            new_access_token = refresh_access_token(refresh_payload)
            
            return True, {
                "user_id": refresh_payload.get("user_id"),
                "username": refresh_payload.get("username"),
                "refresh_needed": True,
                "new_access_token": new_access_token,
            }
    else: # ! NONE OF THE TOKENS ARE PRESENT
        return False, None

    user_id = payload.get("user_id")
    token_uuid = payload.get("uuid")

    # Verify this is the active session for the user
    if token_uuid:
        try:
            # Check if this session is still valid
            response = requests.get(
                f"http://databaseapi:8007/api/player/{user_id}/uuid"
            )
            if response.status_code == 200:
                current_data = response.json()
                current_uuid = current_data.get("uuid")

                # If the UUIDs don't match, this token is from an old session
                if current_uuid and current_uuid != token_uuid:
                    print(
                        f"⚠️ UUID mismatch. Token: {token_uuid}, DB: {current_uuid}",
                        flush=True,
                    )
                    return False, None
        except Exception as e:
            # ! NOTE : Continue with authentication if we can't check the UUID
            print(f"⚠️ Error checking UUID: {str(e)}", flush=True)

    # Return authentication status and user info from the valid access token
    return True, {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
    }

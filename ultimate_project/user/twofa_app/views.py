from django.shortcuts import render

# Create your views here.
import pyotp
import qrcode
import io
import base64
import json
import httpx

# import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TwoFaForm


async def get_user_by_username(username):
    """
    Get user information by username from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://databaseapi:8007/api/player/?username={username}"
            )
            print(
                f"API Response: {response.status_code}, Content: {response.text}",
                flush=True,
            )

            if response.status_code == 200:
                data = response.json()
                print(f"Parsed data type: {type(data)}", flush=True)

                # Check if response is a list (direct array)
                if isinstance(data, list) and len(data) > 0:
                    print(f"Found user in list: {data[0]}", flush=True)
                    return data[0]
                # Check if response has 'results' field (paginated)
                elif (
                    isinstance(data, dict)
                    and data.get("results")
                    and len(data["results"]) > 0
                ):
                    print(f"Found user in results: {data['results'][0]}", flush=True)
                    return data["results"][0]
                else:
                    print(f"No user found for username: {username}", flush=True)

            return None
    except Exception as e:
        print(f"Error getting user by username: {str(e)}", flush=True)
        return None


async def update_user(user_id, data):
    """
    Update user information in the database API
    """
    try:
        print(f"Updating user {user_id} with data: {data}", flush=True)
        async with httpx.AsyncClient() as client:
            # Set content-type header to application/json
            headers = {"Content-Type": "application/json"}

            # Make the PATCH request
            response = await client.patch(
                f"http://databaseapi:8007/api/player/{user_id}/",
                json=data,
                headers=headers,
            )

            print(f"Update response status: {response.status_code}", flush=True)
            print(f"Update response content: {response.text}", flush=True)

            if response.status_code == 200:
                # Try to parse JSON response if available
                try:
                    result = response.json()
                    print(f"User updated successfully: {result}", flush=True)
                    return result
                except ValueError:
                    # If response is not JSON, return True to indicate success
                    print("User updated successfully (non-JSON response)", flush=True)
                    return {"success": True}

            # Log error details
            print(
                f"Error updating user: HTTP {response.status_code} - {response.text}",
                flush=True,
            )
            return None
    except Exception as e:
        print(f"Exception in update_user: {str(e)}", flush=True)
        return None


async def setup_2fa(request):
    try:
        # Get username from the JWT header
        username = request.headers.get("X-Username")
        print(f"Setting up 2FA for user: {username}", flush=True)

        if not username:
            return render(
                request, "twofa_app/error.html", {"error": "User not authenticated"}
            )

        # Get user from database API
        user = await get_user_by_username(username)
        print(f"User data retrieved: {user}", flush=True)

        if not user:
            return render(request, "twofa_app/error.html", {"error": "User not found"})

        # Check if 2FA is already verified
        if user.get("two_fa_enabled"):
            return render(
                request,
                "twofa_app/error.html",
                {"error": "2FA is already enabled for this account"},
            )

        # Generate a new secret for 2FA
        secret = pyotp.random_base32()
        print(f"Generated new 2FA secret: {secret}", flush=True)

        # Save the secret to the user via API
        update_data = {"_two_fa_secret": secret}
        update_result = await update_user(user["id"], update_data)

        if not update_result:
            return render(
                request,
                "twofa_app/error.html",
                {"error": "Failed to update user information. Please try again later."},
            )

        # Generate QR Code URI
        try:
            otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=username, issuer_name="Transcendence"
            )
            print(f"Generated OTP URI: {otp_uri}", flush=True)

            # Generate QR code image
            qr = qrcode.make(otp_uri)
            img_io = io.BytesIO()
            qr.save(img_io, format="PNG")
            img_io.seek(0)

            # Convert to base64 for embedding in HTML
            qr_code_data = base64.b64encode(img_io.getvalue()).decode("utf-8")
            qr_code_img = f"data:image/png;base64,{qr_code_data}"
            print("QR code image generated successfully", flush=True)

            # Create context with the QR code and user info
            context = {
                "username": username,
                "qr_code": qr_code_img,
                "secret": secret,
            }

            return render(request, "twofa_app/setup2fa.html", context)
        except Exception as e:
            print(f"Error generating QR code: {str(e)}", flush=True)
            return render(
                request,
                "twofa_app/error.html",
                {"error": "Error generating 2FA credentials. Please try again."},
            )
    except Exception as e:
        print(f"Error in setup_2fa: {str(e)}", flush=True)
        return render(
            request,
            "twofa_app/error.html",
            {"error": "An unexpected error occurred during 2FA setup."},
        )


async def verify_2fa(request):
    try:
        if request.method == "POST":
            form = TwoFaForm(request.POST)
            username = request.headers.get("X-Username")
            print(f"Verifying 2FA for user: {username}", flush=True)

            if not username:
                return render(
                    request, "twofa_app/error.html", {"error": "User not authenticated"}
                )

            user = await get_user_by_username(username)
            print(f"User data retrieved for verification: {user}", flush=True)

            if not user:
                return render(
                    request, "twofa_app/error.html", {"error": "User not found"}
                )

            if form.is_valid():
                token = request.POST.get("token")
                print(f"Received token: {token}", flush=True)

                # Get the user's secret and verify the token
                # In the API response, the fields are directly accessible as dictionary keys
                secret = user.get("_two_fa_secret")
                if not secret:
                    print("2FA secret not found in user data", flush=True)
                    return render(
                        request,
                        "twofa_app/error.html",
                        {"error": "2FA not set up properly"},
                    )

                print(f"Verifying token with secret: {secret}", flush=True)
                totp = pyotp.TOTP(secret)

                if totp.verify(token):
                    print("Token verification successful", flush=True)
                    # Update user to fully enable 2FA
                    update_data = {"two_fa_enabled": True}
                    update_result = await update_user(user["id"], update_data)

                    if not update_result:
                        print(
                            "Failed to update user 2FA verification status", flush=True
                        )
                        return render(
                            request,
                            "twofa_app/error.html",
                            {
                                "error": "Failed to update 2FA verification status. Please try again later."
                            },
                        )

                    print("2FA setup completed successfully", flush=True)
                    return render(
                        request,
                        "twofa_app/success.html",
                        {"message": "2FA has been successfully set up!"},
                    )
                else:
                    print("Token verification failed", flush=True)
                    form.add_error("token", "Invalid token. Please try again.")
            else:
                print(f"Form validation errors: {form.errors}", flush=True)
        else:
            form = TwoFaForm()
            print("GET request for verify_2fa form", flush=True)

        # If validation fails or it's a GET request, return to the verification page
        return render(
            request, "twofa_app/verify2fa.html", {"form": form, "username": username}
        )
    except Exception as e:
        print(f"Error in verify_2fa: {str(e)}", flush=True)
        return render(
            request,
            "twofa_app/error.html",
            {"error": "An unexpected error occurred during 2FA verification."},
        )


async def disable_2fa(request):
    """
    Verify the user's 2FA token and then disable 2FA for the account
    """
    try:
        # Debug request info
        print(f"==== DISABLE 2FA DEBUG ====", flush=True)
        print(f"Request method: {request.method}", flush=True)
        print(f"Request headers: {dict(request.headers)}", flush=True)
        print(f"Request POST data: {dict(request.POST)}", flush=True)

        # Get username from header
        username = request.headers.get("X-Username")

        if not username:
            print("ERROR: No username found in headers", flush=True)
            return render(
                request,
                "twofa_app/error.html",
                {"error": "User not authenticated: No username found in headers"},
            )

        user = await get_user_by_username(username)
        print(f"User data retrieved for 2FA disabling: {user}", flush=True)

        if not user:
            print(f"ERROR: User {username} not found in database", flush=True)
            return render(
                request,
                "twofa_app/error.html",
                {"error": f"User '{username}' not found in database"},
            )

        # Check if 2FA is actually enabled
        if not user.get("two_fa_enabled"):
            print(f"ERROR: 2FA not enabled for user {username}", flush=True)
            return render(
                request,
                "twofa_app/error.html",
                {"error": "2FA is not enabled for this account"},
            )

        if request.method == "POST":
            print(f"Processing POST request for disable_2fa", flush=True)

            # Get token from POST data directly
            token = request.POST.get("token", "").strip()
            print(f"Received token for 2FA disabling: {token}", flush=True)

            # Basic validation
            if not token:
                print("ERROR: No token provided", flush=True)
                return render(
                    request,
                    "twofa_app/disable2fa.html",
                    {"username": username, "error": "Please enter your 6-digit code"},
                )

            # Validate token format (6 digits)
            if not token.isdigit() or len(token) != 6:
                print(f"ERROR: Invalid token format: {token}", flush=True)
                return render(
                    request,
                    "twofa_app/disable2fa.html",
                    {
                        "username": username,
                        "error": "Please enter a valid 6-digit code",
                    },
                )

            # Get the user's secret and verify the token
            secret = user.get("_two_fa_secret")
            if not secret:
                print("2FA secret not found in user data", flush=True)
                return render(
                    request,
                    "twofa_app/error.html",
                    {"error": "2FA not set up properly: No secret found"},
                )

            print(f"Verifying token with secret: {secret}", flush=True)
            totp = pyotp.TOTP(secret)

            if totp.verify(token):
                print("Token verification successful, disabling 2FA", flush=True)
                # Update user to disable 2FA
                update_data = {
                    "two_fa_enabled": False,
                    "_two_fa_secret": "",  # Clear the secret
                }

                try:
                    update_result = await update_user(user["id"], update_data)
                    print(f"Update result: {update_result}", flush=True)

                    if not update_result:
                        print("Failed to disable 2FA for user", flush=True)
                        return render(
                            request,
                            "twofa_app/error.html",
                            {"error": "Failed to disable 2FA. Please try again later."},
                        )

                    print("2FA disabled successfully", flush=True)
                    return render(
                        request,
                        "twofa_app/success.html",
                        {"message": "2FA has been successfully disabled!"},
                    )
                except Exception as e:
                    print(f"Exception updating user: {str(e)}", flush=True)
                    return render(
                        request,
                        "twofa_app/error.html",
                        {"error": f"Error updating user: {str(e)}"},
                    )
            else:
                print("Token verification failed for 2FA disabling", flush=True)
                return render(
                    request,
                    "twofa_app/disable2fa.html",
                    {"username": username, "error": "Invalid token. Please try again."},
                )
        else:
            # GET request - just show the form
            print("GET request for disable_2fa form", flush=True)

        # If it's a GET request or validation failed, render the form
        return render(request, "twofa_app/disable2fa.html", {"username": username})
    except Exception as e:
        import traceback

        print(f"Error in disable_2fa: {str(e)}", flush=True)
        print(f"Traceback: {traceback.format_exc()}", flush=True)
        return render(
            request,
            "twofa_app/error.html",
            {"error": f"An unexpected error occurred while disabling 2FA: {str(e)}"},
        )

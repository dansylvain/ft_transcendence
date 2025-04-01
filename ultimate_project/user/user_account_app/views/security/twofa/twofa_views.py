import os
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
import pyotp
import qrcode
import io
import base64
import json
import httpx

# import os
from django.contrib.auth.decorators import login_required
from user_account_app.forms.form_two2fa import TwoFaForm

from utils import manage_user_data


async def setup_2fa(request: HttpRequest):
    try:
        # Get username from the JWT header
        username = request.headers.get("X-Username")
        print(f"Setting up 2FA for user: {username}", flush=True)

        if not username:
            return render(
                request, "twofa_app/error.html", {"error": "User not authenticated"}
            )

        # Get user from database API
        user = await manage_user_data.get_user_info_w_username(username)
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
        update_result = await manage_user_data.update_user_w_user_id(user["id"], update_data)

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

async def verify_2fa(request: HttpRequest):
    try:
        if request.method == "POST":
            form = TwoFaForm(request.POST)
            username = request.headers.get("X-Username")
            print(f"Verifying 2FA for user: {username}", flush=True)

            if not username:
                return render(
                    request, "twofa_app/error.html", {"error": "User not authenticated"}
                )

            user = await manage_user_data.get_user_info_w_username(username)
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
                    update_result = await manage_user_data.update_user_w_user_id(user["id"], update_data)

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


async def disable_2fa(request: HttpRequest):
    """
    Verify the user's 2FA token and then disable 2FA for the account
    """
    username = request.headers.get("X-Username")
    try:
        if request.method == "POST":
            form = TwoFaForm(request.POST)
            print(f"Disabling 2FA for user: {username}", flush=True)

            if not username:
                return render(
                    request, "twofa_app/error.html", {"error": "User not authenticated"}
                )

            user = await manage_user_data.get_user_info_w_username(username)
            if not user:
                return render(
                    request, "twofa_app/error.html", {"error": "User not found"}
                )

            if not form.is_valid():
                print(f"ERROR: Form validation failed: {form.errors}", flush=True)
                return render(
                    request, "twofa_app/disable2fa.html", {"username": username, "error": "Form Validation failed"}
                )

            token = request.POST.get("token")
            print(f"Received token: {token}", flush=True)

            if not token:
                print("ERROR: No token provided", flush=True)
                return render(
                    request, "twofa_app/disable2fa.html", {"username": username, "error": "2FA code required"}
                )

            if not token.isdigit() or len(token) != 6:
                print(f"ERROR: Invalid token format: {token}", flush=True)
                return render(
                    request, "twofa_app/disable2fa.html", {"username": username, "error": "Invalid 2FA code"}
                )

            secret = user.get("_two_fa_secret")
            if not secret:
                print("ERROR: 2FA secret not found in user data", flush=True)
                return render(
                    request, "twofa_app/error.html", {"error": "2FA Secret not found on user.database"}
                )

            totp = pyotp.TOTP(secret)
            if not totp.verify(token):
                print("ERROR: Invalid token", flush=True)
                return render(
                    request, "twofa_app/disable2fa.html", {"username": username, "error": "Invalid 2FA code"}
                )

            update_data = {"two_fa_enabled": False, "_two_fa_secret": None}
            update_result = await manage_user_data.update_user_w_user_id(user["id"], update_data)
            if not update_result:
                print("ERROR: Failed to update 2FA status", flush=True)
                return render(
                    request, "twofa_app/disable2fa.html", {"username": username, "error": "Can't update 2FA"}
                )

            print("2FA disabled successfully", flush=True)
            return render(
                request,
                "twofa_app/success.html",
                {"message": "2FA has been successfully disabled!"},
            )
        else:
            print("GET request for disable_2fa form", flush=True)
            return render(request, "twofa_app/disable2fa.html", {"username": username})

    except Exception as e:
        print(f"Error in disable_2fa: {str(e)}", flush=True)
        return render(
            request,
            "twofa_app/error.html",
            {"error": "An unexpected error occurred during 2FA disabling."},
        )

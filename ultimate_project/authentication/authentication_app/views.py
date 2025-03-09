import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from .utils import jwt_required, get_user_from_token


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        otp_code = request.POST.get("otp_code")  # For 2FA

        # Call the database API to verify credentials
        try:
            data = {"username": username, "password": password}

            # Add OTP code if provided
            if otp_code:
                data["otp_code"] = otp_code

            response = requests.post(
                "http://databaseapi:8007/api/verify-credentials/", data=data
            )

            if response.status_code == 200:
                auth_data = response.json()

                # Check if 2FA is required
                if auth_data.get("two_fa_required"):
                    # Store user info in session for 2FA verification
                    request.session["pending_user_id"] = auth_data["user_id"]
                    request.session["pending_username"] = auth_data["username"]

                    # Redirect to 2FA verification page
                    messages.info(request, "Please enter your 2FA code")
                    return render(
                        request,
                        "authentication_app/verify_2fa.html",
                        {"username": auth_data["username"]},
                    )

                # Authentication successful
                # Store user info in session (not the tokens)
                request.session["user_id"] = auth_data["user_id"]
                request.session["username"] = auth_data["username"]

                # Create the response for redirect
                response = redirect("/home/")  # Redirect to static_files home

                # Set JWT tokens in HTTP-only cookies
                response.set_cookie(
                    "access_token",
                    auth_data["access_token"],
                    httponly=True,  # Not accessible via JavaScript
                    secure=settings.SECURE_COOKIES,  # Sent only over HTTPS in production
                    samesite="Lax",  # CSRF protection
                    max_age=60 * 60 * 24,  # 1 day (match your JWT settings)
                )

                response.set_cookie(
                    "refresh_token",
                    auth_data["refresh_token"],
                    httponly=True,
                    secure=settings.SECURE_COOKIES,
                    samesite="Lax",
                    max_age=60 * 60 * 24 * 7,  # 7 days for refresh token
                )

                return response
            else:
                # Authentication failed
                error_data = response.json()
                error_message = error_data.get("error", "Authentication failed")
                messages.error(request, error_message)
                return redirect("/login-form/")  # Redirect back to login form
        except requests.exceptions.RequestException as e:
            # Handle connection errors
            messages.error(request, f"Connection error: {str(e)}")
            return redirect("/login-form/")  # Redirect back to login form

    # For GET requests, redirect to login form
    return redirect("/login-form/")


def logout_view(request):
    # Clear session data
    request.session.flush()

    # Create response for redirect
    response = redirect("/login-form/")  # Redirect to login form

    # Delete JWT cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        enable_2fa = request.POST.get("enable_2fa") == "on"

        # Basic validation
        if password != password_confirm:
            messages.error(request, "Passwords do not match")
            return redirect("/login-form/")  # Redirect back to login form

        # Call the database API to create a new user
        try:
            response = requests.post(
                "http://databaseapi:8007/api/register/",
                data={
                    "username": username,
                    "email": email,
                    "password": password,
                    "enable_2fa": enable_2fa,
                },
            )

            if response.status_code == 201:  # Created
                messages.success(request, "Registration successful! Please log in.")
                return redirect("/login-form/")  # Redirect to login form
            else:
                # Registration failed
                error_data = response.json()
                error_message = error_data.get("error", "Registration failed")
                messages.error(request, error_message)
                return redirect("/login-form/")  # Redirect back to login form
        except requests.exceptions.RequestException as e:
            # Handle connection errors
            messages.error(request, f"Connection error: {str(e)}")
            return redirect("/login-form/")  # Redirect back to login form

    # For GET requests, redirect to login form
    return redirect("/login-form/")


def refresh_token_view(request):
    refresh_token = request.COOKIES.get("refresh_token")

    if not refresh_token:
        return JsonResponse({"error": "Refresh token not found"}, status=401)

    try:
        response = requests.post(
            "http://databaseapi:8007/api/token/refresh/",
            data={"refresh": refresh_token},
        )

        if response.status_code == 200:
            token_data = response.json()

            # Create response
            json_response = JsonResponse({"success": True})

            # Set new access token
            json_response.set_cookie(
                "access_token",
                token_data["access"],
                httponly=True,
                secure=settings.SECURE_COOKIES,
                samesite="Lax",
                max_age=60 * 60 * 24,  # 1 day
            )

            return json_response
        else:
            # Token refresh failed
            return JsonResponse({"error": "Invalid refresh token"}, status=401)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Connection error: {str(e)}"}, status=500)


@jwt_required
def home_view(request):
    # Get the access token from cookies
    access_token = request.COOKIES.get("access_token")

    # Get user info from token
    user_data = get_user_from_token(access_token)

    if not user_data:
        # This shouldn't happen due to the @jwt_required decorator
        return redirect("/login-form/")

    # Redirect to the static_files home page
    return redirect("/home/")


@jwt_required
def setup_2fa_view(request):
    # Get the access token from cookies
    access_token = request.COOKIES.get("access_token")

    # Get user info from token
    user_data = get_user_from_token(access_token)

    if not user_data:
        # This shouldn't happen due to the @jwt_required decorator
        return redirect("/login-form/")

    if request.method == "POST":
        # Enable 2FA for the user
        try:
            response = requests.post(
                "http://databaseapi:8007/api/enable-2fa/",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code == 200:
                data = response.json()

                # Show the QR code and secret
                return render(
                    request,
                    "authentication_app/setup_2fa.html",
                    {
                        "user": user_data,
                        "secret": data["secret"],
                        "qr_code_url": data["qr_code_url"],
                    },
                )
            else:
                messages.error(request, "Failed to enable 2FA")
                return redirect("/home/")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Connection error: {str(e)}")
            return redirect("/home/")

    # For GET requests, show the 2FA setup form
    return render(request, "authentication_app/setup_2fa.html", {"user": user_data})


@jwt_required
def verify_2fa_setup_view(request):
    # Get the access token from cookies
    access_token = request.COOKIES.get("access_token")

    # Get user info from token
    user_data = get_user_from_token(access_token)

    if not user_data:
        # This shouldn't happen due to the @jwt_required decorator
        return redirect("/login-form/")

    if request.method == "POST":
        otp_code = request.POST.get("otp_code")

        if not otp_code:
            messages.error(request, "Please enter the verification code")
            return redirect("setup_2fa")

        # Verify the OTP code
        try:
            response = requests.post(
                "http://databaseapi:8007/api/verify-2fa-setup/",
                headers={"Authorization": f"Bearer {access_token}"},
                data={"otp_code": otp_code},
            )

            if response.status_code == 200:
                messages.success(request, "2FA has been enabled for your account")
                return redirect("/home/")
            else:
                error_data = response.json()
                error_message = error_data.get("error", "Failed to verify 2FA code")
                messages.error(request, error_message)
                return redirect("setup_2fa")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Connection error: {str(e)}")
            return redirect("setup_2fa")

    # For GET requests, redirect to 2FA setup
    return redirect("setup_2fa")

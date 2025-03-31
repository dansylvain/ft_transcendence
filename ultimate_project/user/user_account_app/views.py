import os
import httpx
import pyotp
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import cache_control

from ultimate_project.user.utils.manage_user_data import get_user_info_w_username


@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
async def delete_profile_view(request):

    # Get username from headers
    username = request.headers.get("X-Username")
    if not username:
        return render(
            request,
            "user_management_app/delete-profile.html",
            {"error": "User not authenticated"},
        )

    # Get user data from database API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://databaseapi:8007/api/player/?username={username}"
        )
        # ! Should not happen once the route will be locked
        if response.status_code != 200:
            return render(
                request,
                "user_management_app/delete-profile.html",
                {"user" : user,
                "error": "User not found"},
            )

        # Checking if the user data is a list or a dictionary
        user_data = response.json()
        if isinstance(user_data, list):
            user = user_data[0]
        elif isinstance(user_data, dict) and "results" in user_data:
            user = user_data["results"][0]
        else:
            return render(
                request,
                "user_management_app/delete-profile.html",
                {"user" : user,
                "error": "Invalid user data"},
            )

        if request.method == "GET":
            return render(
                request,
                "user_management_app/delete-profile.html",
                {"user" : user}
            )
        else:
            try:

                # Get form data
                password = request.POST.get("password")
                otp_code = request.POST.get("otp-code")

                if not password:
                    return render(
                        request,
                        "user_management_app/delete-profile.html",
                        {"user" : user,
                        "error": "Password is required"},
                    )

                # Check if 2FA is enabled
                if user.get("two_fa_enabled"):
                    if not otp_code:
                        return render(
                            request,
                            "user_management_app/delete-profile.html",
                            {"user" : user,
                            "error": "2FA code is required"},
                        )

                    # Verify 2FA code
                    secret = user.get("_two_fa_secret")
                    if not secret:
                        return render(
                            request,
                            "user_management_app/delete-profile.html",
                            {"user" : user,
                            "error": "2FA not properly configured"},
                        )

                    totp = pyotp.TOTP(secret)
                    if not totp.verify(otp_code):
                        return render(
                            request,
                            "user_management_app/delete-profile.html",
                            {"user" : user,
                            "error": "Invalid 2FA code"},
                        )

                # AT THIS POINT, 2FA HAS BEEN CHECKED CORRECTLY
                # ! INCORRECT ROUTE
                password_response = await client.post(
                    "http://databaseapi:8007/api/verify-credentials/",
                    data={"username": username, "password": password},
                )

                if password_response.status_code != 200:
                    return render(
                        request,
                        "user_management_app/delete-profile.html",
                        {"user" : user,
                        "error": "Invalid password"},
                    )

                # Delete user
                delete_response = await client.delete(
                    f"http://databaseapi:8007/api/player/{user['id']}/"
                )

                if delete_response.status_code != 204:
                    return render(
                        request,
                        "user_management_app/delete-profile.html",
                        {"user" : user,
                        "error": "Failed to delete user"},
                    )

                # Return success response with redirect URL
                return JsonResponse({"success": True, "redirect_url": "/register/"})

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)




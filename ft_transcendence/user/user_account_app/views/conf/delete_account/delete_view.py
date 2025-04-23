from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import pyotp
from django.http import HttpRequest
#Custom import
from utils import manage_user_data

# === 🔍 Delete user account 🔍 ===

async def handle_post_delete(request: HttpRequest, username, context):
    """Handles POST request for deleting a user."""
    if not username:
        context["error"] = "User not authenticated"
        return render(request, "partials/conf/delete_acc/error_del.html", context), "is_error"
    user = await manage_user_data.get_user_info_w_username(username)
    if not user:
        context["error"] = "We couldn't find a user with the provided information."
        return render(request, "partials/conf/delete_acc/error_del.html", context), "is_error"
    context["user"] = user
    password = request.POST.get("password")
    otp_code = request.POST.get("otp-code")
    if not password:
        context["error_del_page"] = "Please enter your password to delete your account."
        return render(request, "partials/conf/delete_acc/delete_acc.html", context), "is_default"
    if user.get("two_fa_enabled"):
        if not otp_code:
            context["error_del_page"] = "Please enter your 2FA code to delete your account."
            return render(request,"partials/conf/delete_acc/delete_acc.html", context), "is_default"
        secret = user.get("_two_fa_secret")
        if not secret:
            context["error_del_page"] = "2FA is not properly configured: missing secret key."
            return render(request,"partials/conf/delete_acc/delete_acc.html", context), "is_default"
        totp = pyotp.TOTP(secret)
        if not totp.verify(otp_code):
            context["error_del_page"] = "The 2FA code you entered is invalid."
            return render(request,"partials/conf/delete_acc/delete_acc.html", context), "is_default"
    result = await manage_user_data.get_if_user_credentials_valid(username, password)
    if not result or not result.get("success"):
        context["error_del_page"] = "The password you entered is incorrect."
        return render(request,"partials/conf/delete_acc/delete_acc.html", context), "is_default"
    result = await manage_user_data.delete_user_w_user_id(user["id"])
    if not result or not result.get("success"):
        context["error_del_page"] = "Failed to delete your account. Please retry or contact support if the issue persists."
        return render(request,"partials/conf/delete_acc/delete_acc.html", context), "is_default"
    context["message"] = "Your account has been successfully deleted. You will be redirected shortly."
    response = render(request, "partials/conf/delete_acc/success_del.html", context)
    return response, "is_success"

async def handle_get_delete(request, username, context): 
    try:
        if not username:
            context["error"] = "You must be logged in to perform this action. Please log in and try again."
            return render(request, "partials/conf/delete_acc/error_del.html", context), "is_error"
        user = await manage_user_data.get_user_info_w_username(username)
        if not user:
            context["error"] = "We couldn't find a user with the provided information. Please check your credentials and try again."
            return render(request, "partials/conf/delete_acc/error_del.html", context), "is_error"
        context["user"] = user
        return render(request, "partials/conf/delete_acc/delete_acc.html", context), "is_default"
    except Exception as e:
        context["error"] = "Something went wrong when getting the delete page. Please try again later."
        return render(request, "partials/conf/delete_acc/error_del.html", context), "is_error"
    
@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
async def delete_account_view(request: HttpRequest):
    """Main view function that routes requests based on method."""
    context = await manage_user_data.build_context(request)
    try:
        if request.method == "POST":
            response, page_name = await handle_post_delete(request, context["username"], context)
        elif request.method == "GET":
            response, page_name = await handle_get_delete(request, context["username"], context)
        if request.headers.get("HX-Request"):
            if request.headers.get("HX-Target") == "account-content":
                return (response)
        if page_name == "is_error":
            context["page"] = "partials/conf/delete_acc/error_del.html"
        elif page_name == "is_success":
            context["page"] = "partials/conf/delete_acc/success_del.html"
        else:
            context["page"] = "partials/conf/delete_acc/delete_acc.html"     
        return render(request, "layouts/account.html", context)
    except Exception as e:
        print(f"\n❌ Exception in delete_account_view: {e}\n", flush=True)
        if request.headers.get("HX-Request"):
            if request.headers.get("HX-Target") == "account-content":
                return render(request, "partials/conf/delete_acc/error_del.html", context)
        context["page"] = "partials/conf/delete_acc/error_del.html"
        return render(request, "layouts/account.html", context)

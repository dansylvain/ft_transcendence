from django.http import HttpRequest
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from utils import manage_user_data
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import pyotp
from utils import manage_user_data
from user_account_app.forms import custom_form
from django.http import HttpRequest


@require_http_methods(["GET"])
async def profile_vie(request: HttpRequest):
    
    context = await manage_user_data.build_context(request)
    username = context["username"]
    if username:
        user = await manage_user_data.get_user_info_w_username(username)
        if user:
            context["user"] = user
    if request.headers.get("HX-Request"):
        if request.headers.get("HX-Target") == "account-content":
            return render(request, "partials/profile/profile.html", context)
    context["page"] = "partials/profile/profile.html"
    return render(request, "layouts/account.html", context)


# === 🔍 Verifying 2FA for user 🔍 ===

async def handle_post_profile(request: HttpRequest, username, context):
    if not username:
        context["error"] = "User not authenticated"
        return render(request, "partials/profile/error_profile.html", context), True
    user = await manage_user_data.get_user_info_w_username(username)
    if not user:
        context["error"] = "We couldn't find a user with the provided information."
        return render(request, "partials/profile/error_profile.html", context), True
    context["user"] = user
    form_data = {
        "first_name": request.POST.get("first_name", "").strip(),
        "last_name": request.POST.get("last_name", "").strip(),
        "email": request.POST.get("email", "").strip(),
        "username": request.POST.get("username", "").strip(),
    }
    
    update_result = await manage_user_data.update_user_w_user_id(user["id"], form_data)
    if update_result is None:
        context["error"] = "Error when updating user information."
        return render(request, "partials/profile/error_profile.html", context), True
    if not update_result.get("success", True): 
        error_message = update_result.get("error_message", "Failed to update profile. Please try again later.")
        context["error_message"] = error_message
        return render(request, "partials/profile/profile.html", context), False
    new_context = await manage_user_data.build_context(request)
    username = new_context["username"]
    if not username:
        context["error"] = "User not authenticated."
        return render(request, "partials/profile/error_profile.html", context), True
    n_user = await manage_user_data.get_user_info_w_username(username)
    if not n_user:
        context["error"] = "We couldn't find a user with the provided information."
        return render(request, "partials/profile/error_profile.html", context), True
    new_context["user"] = n_user
    new_context["success_message"] = "Profile updated successfully"
    return render(request, "partials/profile/profile.html", new_context), False

async def handle_get_profile(request, username, context):
    if not username:
        context["error"] = "User not authenticated"
        return render(request, "partials/profile/error_profile.html", context), True
    user = await manage_user_data.get_user_info_w_username(username)
    context["user"] = user
    if not user:
        context["error"] = "We couldn't find a user with the provided information."
        return render(request, "partials/profile/error_profile.html", context), True
    return render(request, "partials/profile/profile.html", context), False
    
@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
async def profile_view(request):
    try:
        context = await manage_user_data.build_context(request)
        if request.method == "POST":
            response, is_error_page = await handle_post_profile(request, context["username"], context)
        else:
            response, is_error_page = await handle_get_profile(request, context["username"], context)
        if request.headers.get("HX-Request"):
            if request.headers.get("HX-Target") == "account-content":
                return (response)
        if is_error_page:
            context["page"] = "partials/profile/error_profile.html"
        else:
            context["page"] = "partials/profile/profile.html"        
        return render(request, "layouts/account.html", context)
    except Exception as e:
        print(f"\n❌ Exception in profile_view: {e}\n", flush=True)
        if request.headers.get("HX-Request"):
            if request.headers.get("HX-Target") == "account-content":
                return render(request, "partials/profile/error_profile.html", context)
        context["page"] = "partials/profile/error_profile.html"
        return render(request, "layouts/account.html", context)

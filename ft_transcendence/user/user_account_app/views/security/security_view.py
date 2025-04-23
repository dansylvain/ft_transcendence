from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
# Custom import
from utils import manage_user_data

# === ⭐ Main page security view ⭐ ===

@require_http_methods(["GET"])
async def security_view(request: HttpRequest):
    context = await manage_user_data.build_context(request)
    username = context["username"]
    if username:
        user = await manage_user_data.get_user_info_w_username(username)
        if user:
            context["user"] = user
    if request.headers.get("HX-Request"):
        if request.headers.get("HX-Target") == "account-content":
            return render(request, "partials/security/security.html", context)
    context["page"] = "partials/security/security.html"
    return render(request, "layouts/account.html", context)



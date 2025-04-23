from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_http_methods
from utils import manage_user_data
from django.http import HttpRequest

# === ⭐ Main page confidentiality view ⭐ ===

@require_http_methods(["GET"])
async def conf_view(request: HttpRequest):
    context = await manage_user_data.build_context(request)
    username = context["username"]
    if username:
        user = await manage_user_data.get_user_info_w_username(username)
        if user:
            context["user"] = user
    if request.headers.get("HX-Request"):
        if request.headers.get("HX-Target") == "account-content":
            return render(request, "partials/conf/conf.html", context)
    context["page"] = "partials/conf/conf.html"
    return render(request, "layouts/account.html", context)
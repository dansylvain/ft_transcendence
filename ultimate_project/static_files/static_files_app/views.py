from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

# from django.http import HttpResponse
# from django.template import Context, Template
# from django.middleware import csrf
import requests
import os
import static_files.settings as settings
from django.http import JsonResponse


@never_cache
def index(request):
    # Get username from JWT header if available
    username = request.headers.get("X-Username")

    if "HX-Request" not in request.headers:
        return redirect("/home/")
    obj = {"username": username, "request": request}
    return render(request, "index.html", obj)


# !!      OLD LOGIN PATH AND FORMS
@never_cache
def login_form(request):
    # csrf_token = csrf.get_token(request)
    return render(request, "landing_page.html")


# !!      OLD LOGIN PATH AND FORMS
@never_cache
def login(request):
    # For login page, we don't need to try to get the username from JWT
    # since this page is for unauthenticated users
    obj = {"username": "", "page": "login.html"}
    return render(request, "index.html", obj)


@never_cache
def home(request):
    # Get username from JWT header if available
    username = request.headers.get("X-Username") or request.session.get("username")

    if (
        request.headers.get("HX-Request")
        and request.headers.get("HX-Login-Success") != "true"
    ):
        return render(request, "partials/home.html", {"username": username})

    obj = {"username": username, "page": "partials/home.html"}
    return render(request, "index.html", obj)


# --------------- USER PARTIAL VIEW ----------------

# this two are useless ????? 
@never_cache
def account(request):
    # Get username from JWT header if available
    username = request.headers.get("X-Username") or request.session.get("username")

    if request.headers.get("HX-Request"):
        print("********************\nHTMX REQUEST\n********************", flush=True)
        return render(request, "partials/profile.html", {"username": username})
    print("********************\nNORMAL REQUEST\n********************", flush=True)
    obj = {"username": username, "page": "partials/profile.html"}
    return render(request, "index.html", obj)

@never_cache
def stats(request):
    # Get username from JWT header if available
    username = request.headers.get("X-Username") or request.session.get("username")

    if request.headers.get("HX-Request"):
        print("********************\nHTMX REQUEST\n********************", flush=True)
        return render(request, "partials/stats.html", {"username": username})

    print("********************\nNORMAL REQUEST\n********************", flush=True)
    obj = {"username": username, "page": "partials/stats.html"}
    return render(request, "index.html", obj)


@never_cache
def match_simple_template(request, user_id):
    url = f"http://tournament:8001/tournament/simple-match/{user_id}/"
    print(f"###################### userid {user_id} #################", flush=True)
    page_html = requests.get(url).text

    # Get username from JWT header if available
    username = request.headers.get("X-Username") or request.session.get("username")

    return render(
        request,
        "index.html",
        {
            "username": username,
            "rasp": os.getenv("rasp", "false"),
            "pidom": os.getenv("pi_domain", "localhost:8443"),
            # "simpleUsers": consumer.players,
            "page": page_html,
        },
    )


@never_cache
def tournament_template(request, user_id):
    url = f"http://tournament:8001/tournament/tournament/{user_id}/"
    print(f"###################### userid {user_id} #################", flush=True)
    page_html = requests.get(url).text

    # Get username from JWT header if available
    username = request.headers.get("X-Username") or request.session.get("username")

    return render(
        request,
        "index.html",
        {
            "username": username,
            "rasp": os.getenv("rasp", "false"),
            "pidom": os.getenv("pi_domain", "localhost:8443"),
            # "simpleUsers": consumer.players,
            "page": page_html,
        },
    )

@never_cache
def reload_template(request):
    
    """
    The purpose of `reload_template` is to enable full page reloading while serving 
    dynamic content through the static container. 

    This function is specifically triggered when a service is requested to be served 
    through the static container, as defined in the `reverse_proxy_request` function 
    of the FastAPI app. 
    
    """
    headers = {key: value for key, value in request.headers.items()}

    url = headers["X-Url-To-Reload"]
    print(f"\n\nprint {url}\n\n", flush=True)
    page_html = requests.get(url, headers=headers).text

    # Get username from JWT header if available
    username = request.headers.get("X-Username") or request.session.get("username")
    
    print("********************\nTEMPLATE REQUEST\n********************", flush=True)

    return render(
        request,
        "index.html",
        {
            "username": username,
            "rasp": os.getenv("rasp", "false"),
            "pidom": os.getenv("pi_domain", "localhost:8443"),
            "page": page_html,
        },
    )


@never_cache
def translations(request, lang):
    try:
        file_path = os.path.join(
            settings.BASE_DIR,
            "static_files_app",
            "static",
            "translations",
            f"{lang}.json",
        )
        with open(file_path, "r") as file:
            return JsonResponse(file.read(), safe=False)
    except FileNotFoundError:
        return JsonResponse({"error": "File not found"}, status=404)


@never_cache
def register(request):
    # Get username from JWT header if available
    username = request.headers.get("X-Username") or request.session.get("username")

    obj = {"username": username, "page": "register.html"}
    return render(request, "index.html", obj)


@never_cache
def forgotPassword(request):
    # Get username from JWT header if available
    username = request.headers.get("X-Username") or request.session.get("username")

    obj = {"username": username, "page": "forgot-password.html"}
    return render(request, "index.html", obj)


@never_cache
def twoFactorAuth(request):
    # Try to get username from multiple sources
    username = request.headers.get("X-Username") or request.session.get("username")

    # Check if username is in the query parameters (takes precedence)
    query_username = request.GET.get("username")
    if query_username:
        print(f"Found username in query parameters: {query_username}", flush=True)
        username = query_username

    print(f"Using username for 2FA page: {username}", flush=True)

    # If it's an HTMX request, just render the partial template
    if "HX-Request" in request.headers:
        return render(request, "two-factor-auth.html", {"username": username})

    # Otherwise render the full page
    obj = {"username": username, "page": "two-factor-auth.html"}
    return render(request, "index.html", obj)

@csrf_exempt    
@never_cache
def error(request, code=404):  # Code 404 par défaut
    username = request.session.get("username")
    obj = {"username": username, "status_code": code, "page": "error.html"}
    return render(request, "index.html", obj)

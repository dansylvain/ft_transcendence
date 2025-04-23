from fastapi import FastAPI, Request, HTTPException, Response, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)
import httpx
import logging
import json
import re

# Custom Imports
import authentication as auth
from auth_validators import is_authenticated
from csrf_tokens import csrf_validator


# =================== 🚀 FastAPI Application Setup for API Gateway 🚀 ============

app = FastAPI(
    title="API Gateway",
    description="This API Gateway routes requests to various microservices. \
        Define endpoints to get any data here :)",
    version="1.0.0",
    docs_url=None, # ! Comment this line to enable access to SwaggerUI
)

# ======================= 🚀 SERVICES TO BE SERVED BY FASTAPI 🚀 =================

services = {
    "tournament": "http://tournament:8001",
    "match": "http://match:8002",
    "static_files": "http://static_files:8003",
    "user": "http://user:8004",
    "databaseapi": "http://databaseapi:8007",
}

# ============================= 📜 LOGGER CONFIGURATION 📜 =======================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =================== 📜 REGEX PATHS FOR BOUNDER MIDDLEWARE📜 ====================

AUTH_PATH = [
    r"^/login/?$",
    r"^/register/?$",
    r"^/auth/login/?$",
    r"^/auth/register/?$",
    r"^/two-factor-auth/?$",
    r"^/auth/verify-2fa/?$",
    r"/api/player/\d+/uuid",
    r"^/api/check-2fa/?$",
]

EXCLUDED_PATH = [
    r"^/favicon.ico/?$",
    r"^/translations/[a-z]{2}.json/?$",
    r"^/match/stop-match/undefined/undefined/?$",
    r"^/match/stop-match/\d+/undefined/?$",

    # SwaggerUI related routes
    r"^/docs/?$",
    r"^/openapi.json/?$",
    r"^/redoc/?$",
]

KNOWN_PATHS = [
    r"^/login/?$",
    r"^/register/?$",
    r"^/home/?$",
    r"^/two-factor-auth/?$",
    r"^/tournament/simple-match/.*$",
    r"^/tournament/tournament/.*$",
    r"^/account/.*$",
]


@app.middleware("http")
async def bouncer_middleware(request: Request, call_next):
    print( f"======== 👮 URL ENTERING BOUNCER = {request.url.path} ============\n")
    print(f"======== 👮 COOKIES ENTERING BOUNCER = {request.cookies} ============\n")

    is_auth, user_info = is_authenticated(request)
    is_csrf_valid = csrf_validator(request)
    
    # Let go through the Middleware everyting included in EXCLUDED_PATH
    if any(re.match(pattern, request.url.path) for pattern in EXCLUDED_PATH):
        print(f"\n👍 Bounder Middleware non trigered 👍\n")
        response = await call_next(request)
        return response
    
    # Check if path starts with an AUTH_PATH pattern but doesn't exactly match any known pattern
    if not is_auth and not any(re.match(pattern, request.url.path) for pattern in AUTH_PATH):
        
        # First check if this path starts with any AUTH_PATH pattern but doesn't match any KNOWN_PATHS
        if any(request.url.path.startswith(pattern.replace(r'^', '').replace(r'/?$', '')) for pattern in AUTH_PATH) and \
           not any(re.match(pattern, request.url.path) for pattern in KNOWN_PATHS):
            print(f"⛔ Path starts with auth path but is invalid: {request.url.path} ⛔")
            exc = StarletteHTTPException(status_code=404, detail="Not Found")
            return await http_exception_handler(request, exc)
            
    # User request an AUTH_PATH while being authenticated.
    if (is_auth) and any(re.match(pattern, request.url.path) for pattern in AUTH_PATH):
        print(f"\n⬅️ Authenticated user request auth pages, redirecting to home ⬅️\n")
        
        if "HX-Request" in request.headers:
            response = Response(status_code=200)
            response.headers["HX-Location"] = ("/home/")
        else:
            response = RedirectResponse(url="/home/")
        return response

    # User request a regular page while not being authenticated
    elif (not is_auth or not is_csrf_valid) and not any(re.match(pattern, request.url.path) for pattern in AUTH_PATH):
        print(f"\n⛔ Bounder Middleware Trigerred, non auth request ⛔\n")
        # Check if this is an HTMX request
        if "HX-Request" in request.headers:
            response = Response(status_code=200)
            response.headers["HX-Location"] = "/register/"
            
            # Clear JWT cookies
            response.delete_cookie(key="access_token", path="/")
            response.delete_cookie(key="refresh_token", path="/")
            response.delete_cookie(key="csrftoken", path="/")
        else:
            response = RedirectResponse(url="/register/")
            
            # Clear JWT cookies
            response.delete_cookie(key="access_token", path="/")
            response.delete_cookie(key="refresh_token", path="/")
            response.delete_cookie(key="csrftoken", path="/")
        return response

    print(f"👍 Bounder Middleware non trigered 👍")

    response = await call_next(request)
    return response


# ============================== 🌟 FASTAPI MIDDLEWARE 🌟 ========================

# Current middleware chain
# 1️⃣ - Client sends an HTTP request.
# 2️⃣ - CORS Middleware processes the request first (since it's declared first).
# 3️⃣ - Token Refresh Middleware runs next and calls call_next(request), passing the request to the route handler.
# 4️⃣ - Route Handler (your actual API logic) processes the request and generates a response.
# 5️⃣ - The response flows back:
#
#     5️⃣.1️⃣ - goes back through the Token Refresh Middleware,
#     which may modify it (e.g., refreshing tokens)
#     5️⃣.2️⃣ - continues back to the client.

# Middleware in FastAPI runs in the order they are declared in this file.
# Be mindful of the order when adding class-based and function-based
# middleware.
# Configuring CORS middleware  below:
# [Middleware n°1]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow only trusted origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-CSRFToken", "Set-Cookie"],
)


@app.middleware("http")
async def jwt_refresh_middleware(request: Request, call_next):
    
    response = await call_next(request)
    is_auth, user_info = is_authenticated(request)

    # If authenticated and token `refresh_needed` is here : generate a new `access_token`
    if is_auth and user_info and user_info.get("refresh_needed"):
        print("🔄 JWT Refresh Middleware Trigerred: Refreshing access token", flush=True)
        
        # Set the new access token in the response
        response.set_cookie(
            key="access_token",
            value=user_info.get("new_access_token"),
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 2,  # new access_token == 2hours, just like the regular one
        )
    return response


# This middleware suppress nginx warning about different timestamps between fastAPI and ngninx
@app.middleware("http")
async def clean_duplicate_headers_middleware(request: Request, call_next):
    response = await call_next(request)

    # Copy headers...
    headers_dict = dict(response.headers.items())

    # ... and remove duplicate headers that cause nginx warnings
    if "server" in headers_dict:
        del response.headers["server"]
    if "date" in headers_dict:
        del response.headers["date"]

    return response


# =========================== ⚠️ Exception Handling ⚠️ ===========================

# When an exception of type StarletteHTTPException is raised during
# the processing of a request, the custom exception handler
# defined under this decorator will be calleD
# If you have multiple exception handlers for the same exception in
# FastAPI, only the first one registered will be used.
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return await reverse_proxy_handler(
        "static_files", f"error/{exc.status_code}/", request
    )


# ========= 🛠️ Main Function Handling the Reverse Proxy for the Route 🛠️ =========


async def reverse_proxy_handler(
    target_service: str,
    incoming_path: str,
    request: Request,
    serve_from_static: bool = False,
    static_service_name: str = None,
):
    """
     Proxies a request either directly to a target service container or through
     a static service container, which then serves the content.

     - If `use_static_reload` is **False**, the request is forwarded directly to
     the target service.
     - If `use_static_reload` is **True**, the request is first routed through the
     static service container, using the reload-template/ default URL.
     The static container then forwards the request to the target service,
     retrieves the response, and serves it back, enabling full-page reloads.
     - Use the bool is single page if you want to use the index.html
         or not
     If you need to call a custom URL within the static container, simply
     call the static service directly and use a URL defined in its
    `urls.py`, just as you would when calling any other service.

     Using the static service container allows for a **full page reload**,
     ensuring that  static assets like CSS, JavaScript, and HTML templates
     are properly served and updated.
    """
    # Validate the target service
    if target_service not in services:
        raise HTTPException(status_code=404, detail="Requested service not found.")
    # Validate the static service if `serve_from_static` is enabled
    if serve_from_static:
        if not static_service_name or static_service_name not in services:
            raise HTTPException(
                status_code=400, detail="Invalid or missing static service."
            )
    async with httpx.AsyncClient(follow_redirects=True) as client:
        base_service_url = services[target_service].rstrip("/")
        normalized_path = incoming_path.lstrip("/")
        # Handle query parameters
        query_params = request.query_params
        query_string = f"?{query_params}" if query_params else ""
        if target_service == static_service_name:
            print(
                "⚠️ Request is for the static service, but it's specified to \
                be served by the same static service directly. Default \
                will directly call the static service. ⚠️"
            )
        forwarded_headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() != "host"
        }
        forwarded_headers["Host"] = "localhost"
        # Construct request URL
        # If serve_from_static is enabled and the requested service is not
        # already the static service,the request will be routed through the
        # reload-template for full-page reloading.
        if serve_from_static and target_service != static_service_name:
            static_service_url = services[static_service_name].rstrip("/")
            final_url = f"{static_service_url}/reload-template/"
            forwarded_headers["X-Url-To-Reload"] = (
                f"{base_service_url}/{normalized_path}{query_string}"
            )
        else:
            final_url = f"{base_service_url}/{normalized_path}{query_string}"
        # Debug logging
        print("\n" + "=" * 50)
        print(f"🔁 PROXY REQUEST INITIATED 🔁")
        print("=" * 50)
        print(f"🔄 Request Method: {request.method}")
        print(f"🔗 Target URL: {final_url}")
        print(f"📩 Query Parameters: {query_string if query_string else 'None'}")
        print(
            f"🛡️ HX-Request Present: {'✅ Yes' if 'HX-Request' in request.headers else '❌ No'}"
        )
        print(
            f"📦 Using Static container for reload: {'✅ Yes' if serve_from_static else '❌ No'}"
        )
        print("=" * 50 + "\n", flush=True)
        # Check user authentication and attach user info headers
        is_authenticated_user, user_info = is_authenticated(request)
        if is_authenticated_user and user_info:
            print("🔑 ==== IS AUTHENTICATED ==== \n", flush=True)
            forwarded_headers["X-User-ID"] = str(user_info.get("user_id", ""))
            forwarded_headers["X-Username"] = user_info.get("username", "")
        # Debug log cookies
        # print("=" * 50 + "\n", flush=True)
        # print(f"🔑 Forwarding headers:", flush=True)
        # for key, value in forwarded_headers.items():
        #     print(f"{key}: {value}", flush=True)
        # print("=" * 50 + "\n", flush=True)
        # print(f"🍪 Forwarding cookies: {request.cookies}", flush=True)
        request_cookies = request.cookies
        request_method = request.method
        request_body = await request.body()
        try:
            response = await client.request(
                request_method,
                final_url,
                headers=forwarded_headers,
                content=request_body,
                cookies=request_cookies,
            )
            print("\n\n========== RESPONSE DEBUG ==========\n", flush=True)
            print(f"🔗 Final URL: {final_url}", flush=True)
            print(f"🔄 Status Code: {response.status_code}", flush=True)
            # print(f"📩 Headers:\n{response.headers}", flush=True)
            print("\n====================================\n", flush=True)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                f"❌ Request failed with status code {exc.response.status_code}"
            )
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.response.text
            )
        except httpx.RequestError as exc:
            logger.error(f"❌ Request error: {exc}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    response_headers = {key: value for key, value in response.headers.items()}
    response_headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
        media_type=content_type or "text/html; charset=utf-8"
    )


# ============================ 🏠 REDIRECT TO HOME 🏠 ============================

@app.get("/")
async def redirect_to_home():
    return RedirectResponse(url="/home/")

# ========================= 🏆 Tournament Route Setup 🏆 =========================


@app.api_route("/tournament/tournament-pattern/{tournament_id:int}/", methods=["GET"])
async def tournament_pattern_proxy(tournament_id, request: Request):
    print("################## NEW ROUTE USED #######################", flush=True)
    print(f"################## NEW ROUTE USED ##########{tournament_id}", flush=True)
    return await reverse_proxy_handler(
        "tournament", f"tournament/tournament-pattern/{tournament_id}/", request
    )


@app.api_route("/tournament/{path:path}", methods=["GET"])
async def tournament_proxy(path: str, request: Request):
    """
    Proxy requests to the tournament microservice.

    - **path**: The path to the resource in the tournament service.
    - **request**: The incoming request object.
    - **Headers**:
      - `HX-Request`: If present, the request is treated as an HTMX request.
    - **Responses**:
      - Returns the content from the tournament microservice.
      - If `path` is "simple-match/", returns specific content.
    """

    is_auth, user_info = is_authenticated(request)

    if is_auth:
        user_id = user_info.get("user_id")
    else:
        user_id = 0

    print(
        "################## NEW USER CREATED #######################",
        user_id,
        flush=True,
    )
    print(path + str(user_id) + "/")

    if "HX-Request" in request.headers and "HX-Login-Success" not in request.headers:
        return await reverse_proxy_handler(
            "tournament", "tournament/" + path + str(user_id) + "/", request
        )
    elif path == "simple-match/":
        return await reverse_proxy_handler(
            "static_files", "/tournament-match-wrapper/" + str(user_id) + "/", request
        )
    elif path == "tournament/":
        return await reverse_proxy_handler(
            "static_files", "/tournament-wrapper/" + str(user_id) + "/", request
        )
    else:
        error_message = "Page Not Found"
        return await reverse_proxy_handler("static_files", "error/", request)


# =============================== ⚽ MATCH ROUTE ⚽ ==============================


@app.api_route("/match/stop-match/{path:path}", methods=["GET"])
async def stop_match_proxy(path: str, request: Request):
    """
    Proxy requests to the match microservice.

    - **path**: The path to the resource in the match service.
    - **request**: The incoming request object.
    - **Query Parameters**:
      - `matchId`: The match identifier (optional).
      - `playerId`: The player identifier (optional).
    - **Responses**:
      - Returns the content from the match microservice.
    """
    return await reverse_proxy_handler("match", "/match/stop-match/" + path, request)


@app.api_route("/match/match3d/{path:path}", methods=["GET"])
async def match_proxy(
    path: str,
    request: Request,
    matchId: int = Query(None),
    playerId: int = Query(None),
):
    """
    Proxy requests to the match microservice.

    - **path**: The path to the resource in the match service.
    - **request**: The incoming request object.
    - **Query Parameters**:
      - `matchId`: The match identifier (optional).
      - `playerId`: The player identifier (optional).
    - **Responses**:
      - Returns the content from the match microservice.
    """
    path = (
        f"match/match3d/?matchId={matchId}&playerId={playerId}"
        if matchId is not None and playerId is not None
        else "match/"
    )

    return await reverse_proxy_handler("match", path, request)


@app.api_route("/match/match2d/{path:path}", methods=["GET"])
async def match_proxy(
    path: str,
    request: Request,
    matchId: int = Query(None),
    playerId: int = Query(None),
    playerName: str = Query(None),
    player2Id: int = Query(None),
    player2Name: str = Query(None),
):
    """
    Proxy requests to the match microservice.

    - **path**: The path to the resource in the match service.
    - **request**: The incoming request object.
    - **Query Parameters**:
      - `matchId`: The match identifier (optional).
      - `playerId`: The player identifier (optional).
    - **Responses**:
      - Returns the content from the match microservice.
    """
    path = (
        f"match/match2d/?matchId={matchId}&playerId={playerId}&playerName={playerName}&player2Id={player2Id}&player2Name={player2Name}"
        if matchId is not None and playerId is not None
        else "match/"
    )

    return await reverse_proxy_handler("match", path, request)
    # elif path == "simple-match/":
    #     return await proxy_request("static_files", "/home/", request)


# =========================== 🚀 USER SERVICE ROUTE 🚀 ===========================


# WILL BE SUED INT EH FURTUR FOR THE FRIENDSHIP SYSTEM
@app.api_route("/user/{path:path}", methods=["GET"])
async def user_route(path: str, request: Request):

    # see if need to fix header hx login sucess
    if "HX-Request" in request.headers and "HX-Login-Success" not in request.headers:
        return await reverse_proxy_handler("user", "/user/" + path, request)
    else:
        return await reverse_proxy_handler(
            "user",
            "/user/" + path,
            request,
            serve_from_static=True,
            static_service_name="static_files",
        )


# OK
# handle the user account management
@app.api_route("/account/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_account_route(path: str, request: Request):

    # see if need to fix header hx login sucess
    if "HX-Request" in request.headers and "HX-Login-Success" not in request.headers:
        return await reverse_proxy_handler("user", "/account/" + path, request)
    else:
        return await reverse_proxy_handler(
            "user",
            "/account/" + path,
            request,
            serve_from_static=True,
            static_service_name="static_files",
        )


# =========================== 🗂️ API DATABASE PROXY 🗂️ ===========================


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def databaseapi_proxy(path: str, request: Request):
    """
    Proxy requests to the database API microservice.

    - **path**: The path to the resource in the database API

    ### GET Examples:
    - **List all players**: GET /api/player/
    - **Get player by ID**: GET /api/player/1/
    - **Filter players by username**: GET /api/player/?username=player1
    - **Filter players by email**: GET /api/player/?email=example

    - **List all tournaments**: GET /api/tournament/
    - **Get tournament by ID**: GET /api/tournament/1/

    - **List all matches**: GET /api/match/
    - **Get match by ID**: GET /api/match/1/
    - **Filter matches by player**: GET /api/match/?player1=1
    - **Filter matches by tournament**: GET /api/match/?tournament=1

    ### POST Examples:
    - **Create a new player**: POST /api/player/
    - **Create a new tournament**: POST /api/tournament/
    - **Create a new match**: POST /api/match/

    ### Pagination:
    - All list endpoints are paginated with 10 items per page
    - **Navigate pages**: GET /api/player/?page=2

    ### Check 2FA:
    - **Check 2FA**: POST /api/check-2fa/
    - **Body**:
      - `username`: The username of the user
      - `password`: The password of the user
    - **Responses**:
      - `200 OK`: The user is authenticated and 2FA is not enabled
      - `401 Unauthorized`: The user is authenticated but 2FA is enabled
    """
    return await reverse_proxy_handler("databaseapi", f"api/{path}", request)


# ========================== 📜 AUTHENTICATION ROUTE 📜 ==========================


@app.api_route("/login/{path:path}", methods=["GET"])
@app.api_route("/login", methods=["GET"])
async def login_page_route(request: Request, path: str = ""):
    return await reverse_proxy_handler("static_files", "login/", request)


@app.api_route("/auth/login", methods=["POST"])
@app.api_route("/auth/login/", methods=["POST"])
async def login_page_route(request: Request):
    form_data = await request.form()  # Extract form data
    username = form_data.get("username")
    password = form_data.get("password")

    # Create a new response object
    response = Response()

    return await auth.login_fastAPI(request, response, username, password)


# Add logout endpoint
@app.api_route("/auth/logout", methods=["POST"])
@app.api_route("/auth/logout/", methods=["POST"])
async def logout_route(request: Request):
    return await auth.logout_fastAPI(request)


@app.api_route("/register/{path:path}", methods=["GET"])
@app.api_route("/register", methods=["GET"])
async def register_page_route(request: Request, path: str = ""):
    return await reverse_proxy_handler("static_files", "register/", request)


@app.api_route("/auth/register", methods=["POST"])
@app.api_route("/auth/register/", methods=["POST"])
async def register_page_route(request: Request):
    form_data = await request.form()  # Extract form data

    first_name = form_data.get("first_name")
    last_name = form_data.get("last_name")
    username = form_data.get("username")
    password = form_data.get("password")
    email = form_data.get("email")

    # Create a new response object
    response = Response()

    return await auth.register_fastAPI(
        request, response, username, password, email, first_name, last_name
    )


@app.api_route("/two-factor-auth/", methods=["GET"])
async def two_factor_auth_proxy(request: Request):

    # If we have a username in the query parameters, make sure it's passed to the template
    query_params = request.query_params
    username = query_params.get("username")
    if username:
        # append username to the path
        return await reverse_proxy_handler(
            "static_files", f"two-factor-auth/?username={username}", request)

    # Forward the request to the static_files container
    return await reverse_proxy_handler("static_files", "two-factor-auth/", request)


# used to verify two fa login
@app.api_route("/auth/verify-2fa/", methods=["POST"])
async def verify_2fa_login(request: Request):
    
    # print("Processing 2FA verification during login", flush=True)

    # Get the form data
    form_data = await request.form()

    token = form_data.get("token")
    username = form_data.get("username")

    # Create a new response object
    response = Response()

    # Process the 2FA verification and generate JWT
    return await auth.verify_2fa_and_login(request, response, username, token)


@app.api_route("/{path:path}", methods=["GET"])
async def static_files_proxy(path: str, request: Request):
    """
    Proxy requests to the static files microservice.

    THE SPA'S INDEX.HTML FILE IS HERE!!!

    - **path**: The path to the resource in the static files service.
    - **request**: The incoming request object.
    """

    return await reverse_proxy_handler("static_files", path, request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)

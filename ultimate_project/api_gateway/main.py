from fastapi import FastAPI, Request, HTTPException, Response, Depends, Query
import httpx
import logging
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from itsdangerous import URLSafeTimedSerializer
from starlette.exceptions import HTTPException as StarletteHTTPException  # If you need to use it
import secrets
import hashlib
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json


# from fastapi.middleware.cors import CORSMiddleware
from utils import auth_helpers, authentication, cookies_helpers

# useful ?
templates = Jinja2Templates(directory="templates")

# ======= 🚀 FastAPI Application Setup for API Gateway 🚀 =======

app = FastAPI(
    title="API Gateway",
    description="This API Gateway routes requests to various microservices. \
        Define endpoints to get any data here :)",
    version="1.0.0",
)

# ====== 🚀 SERVICES TO BE SERVED BY FASTAPI 🚀 ======

services = {
    "tournament": "http://tournament:8001",
    "match": "http://match:8002",
    "static_files": "http://static_files:8003",
    "user": "http://user:8004",
    "databaseapi": "http://databaseapi:8007",
}

# ====== 📜 LOGGER CONFIGURATION 📜 ======

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== 🌟 FASTAPI MIDDLEWARE 🌟 ======

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

# 🔄 Token Refresh Middleware for HTTP Requests  
# 🏗️ Function-Based Middleware
# [Middleware n°2]
@app.middleware("http")
async def token_refresh_middleware(request: Request, call_next):
    """
    Middleware that checks if the access token needs to be refreshed.
    If refresh is needed, it adds the new access token to the response.
    """
    # First process the request normally
    # call_next() will call the next middleware / if none call
    # the actual route 
    response = await call_next(request)

    # Check authentication status after request processing
    is_auth, user_info = authentication.is_authenticated(request)

    # If authenticated and token refresh needed, update the response 
    # cookies
    if is_auth and user_info and user_info.get("refresh_needed"):
        print("🔄 Middleware: Refreshing access token", flush=True)
        # Set the new access token in the response
        response.set_cookie(
            key="access_token",
            value=user_info.get("new_access_token"),
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 6,  # 6 hours
        )
    return (response)

# Middleware to set and validate CSRF tokens
# [Middleware n°3]
CSRF_SECRET = os.getenv("CSRF_SECRET_KEY")
csrf_serializer = URLSafeTimedSerializer(CSRF_SECRET, salt=secrets.token_urlsafe(16))
class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # If it's a GET request, we generate a CSRF token and set the cookie
        # If it's a GET request and no token exists, generate a new one
        if "csrftoken" not in request.cookies:
            csrf_token = self.generate_csrf_token()
            response = await call_next(request)
            response.set_cookie(
                key="csrftoken", 
                value=csrf_token, 
                httponly=True, 
                secure=True, 
                samesite="None", 
                path="/", 
                max_age=60 * 60 * 6  # 6 hours
            )
            return (response)
        
        # For POST requests, validate the CSRF token
        if request.method == "POST":
            
            # INT HE FTUIRE CHECK IF JWT FOR INETRNAL POST/DELTE/PUT
            # ELSE CHECK
           """  csrf_token_from_header = request.headers.get("X-CSRFToken")
            csrf_token_from_cookie = request.cookies.get("csrftoken")
            # Validate the token
            print(f"\n == CSRF token from header: {csrf_token_from_header} == \n", flush=True)
            print(f"\n == CSRF token from cookie: {csrf_token_from_cookie} == \n", flush=True)
            if not csrf_token_from_header or csrf_token_from_header != csrf_token_from_cookie:
                raise HTTPException(status_code=403, detail="Forbidden (CSRF token mismatch)") """
        return await call_next(request)

    def generate_csrf_token(self):
        """Generate a CSRF token."""
        secret = secrets.token_hex(32)  # 32-byte secret key
        hashed_token = hashlib.sha256(secret.encode()).hexdigest()
        return hashed_token
app.add_middleware(CSRFMiddleware)

# This middleware is used to debug incoming cookies in FastAPI.
# It prints the incoming cookies to the console for debugging purposes.
# [Middleware n°4]
@app.middleware("http")
async def debug_cookies_middleware(request: Request, call_next):
    print(f"🔍 Incoming Cookies in FastAPI: {request.cookies}", flush=True)
    response = await call_next(request)
    if "set-cookie" in response.headers:
        set_cookie_headers = response.headers.getlist("set-cookie")
        for cookie in set_cookie_headers:
            print(f"🔍 Outgoing Set-Cookie header: {cookie}", flush=True)
    return (response)

""" @app.middleware("http")
async def debug_full_response_middleware(request: Request, call_next):
    print(f"🔍 Incoming Request: {request.method} {request.url}", flush=True)
    response = await call_next(request)
    # Print full response details (headers, status code, and body)
    print(f"🔍 Outgoing Response Status: {response.status_code}", flush=True)
    print(f"🔍 Response Headers: {response.headers}", flush=True)
    try:
        if response.headers.get("Content-Type") == "application/json":
            response_body = await response.json()
            print(f"🔍 Response Body (JSON): {response_body}", flush=True)
        else:
            # Print raw content for non-JSON responses (e.g., HTML or plain text)
            response_body = await response.body()
            print(f"🔍 Response Body (Raw): {response_body.decode()}", flush=True)
    except Exception as e:
        print(f"🚨 Error parsing response body: {e}", flush=True)
    return response """

# ===== ⚠️ Exception Handling ⚠️ =====

# When an exception of type StarletteHTTPException is raised during 
# the processing of a request, the custom exception handler 
# defined under this decorator will be calleD
# If you have multiple exception handlers for the same exception in
# FastAPI, only the first one registered will be used.
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return await reverse_proxy_handler("static_files", f"error/{exc.status_code}/", request)

# ======= 🛠️ Main Function Handling the Reverse Proxy for the Route 🛠️ =======

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN")

def validate_internal_token(request: Request) -> bool:
    internal_token = request.headers.get("X-Internal-Token")
    print(f"\n\n VALIDATE TOKEN: {internal_token}\n\n", flush=True)
    if not internal_token:
        return None
    return internal_token == INTERNAL_TOKEN

async def reverse_proxy_handler(target_service: str, incoming_path: str, request: Request,
            serve_from_static: bool = False, static_service_name: str = None,
            is_full_page: bool = False):
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
            raise HTTPException(status_code=400, detail="Invalid or missing static service.")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        base_service_url = services[target_service].rstrip("/")
        normalized_path = incoming_path.lstrip("/")
        # Handle query parameters
        query_params = request.query_params
        query_string = f"?{query_params}" if query_params else ""
        if target_service == static_service_name:
            print("⚠️ Request is for the static service, but it's specified to \
                be served by the same static service directly. Default \
                will directly call the static service. ⚠️")
        
        forwarded_headers = {
            key: value for key, value in request.headers.items() if key.lower() != "host"
        }
        forwarded_headers["Host"] = "localhost"
        # Construct request URL
        # If serve_from_static is enabled and the requested service is not 
        # already the static service,the request will be routed through the 
        # reload-template for full-page reloading.
        if serve_from_static and target_service != static_service_name:
            static_service_url = services[static_service_name].rstrip("/")
            final_url = f"{static_service_url}/reload-template/"
            forwarded_headers["X-Url-To-Reload"] = f"{base_service_url}/{normalized_path}{query_string}"
        else:
            final_url = f"{base_service_url}/{normalized_path}{query_string}"
        if is_full_page:
            forwarded_headers["X-Is-Full-Page"] = "True"

        # Debug logging
        print("\n" + "=" * 50)
        print(f"🔁 PROXY REQUEST INITIATED 🔁")
        print("=" * 50)
        print(f"🔄 Request Method: {request.method}")
        print(f"🔗 Target URL: {final_url}")
        print(f"📩 Query Parameters: {query_string if query_string else 'None'}")
        print(f"🛡️ HX-Request Present: {'✅ Yes' if 'HX-Request' in request.headers else '❌ No'}")
        print(f"📦 Using Static container for reload: {'✅ Yes' if serve_from_static else '❌ No'}")
        print("=" * 50 + "\n", flush=True)
            
        # Check user authentication and attach user info headers
        is_authenticated_user, user_info = authentication.is_authenticated(request)
        if is_authenticated_user and user_info:
            print("🔑 ==== IS AUTHENTICATED ==== \n", flush=True)
            forwarded_headers["X-User-ID"] = str(user_info.get("user_id", ""))
            forwarded_headers["X-Username"] = user_info.get("username", "")

        # Debug log cookies
        print("=" * 50 + "\n", flush=True)
        print(f"🔑 Forwarding headers:", flush=True)
        for key, value in forwarded_headers.items():
            print(f"{key}: {value}", flush=True)
        print("=" * 50 + "\n", flush=True)
        print(f"🍪 Forwarding cookies: {request.cookies}", flush=True)

        request_method = request.method
        # need to add a try here
        request_body = await request.body()
        request_cookies = request.cookies
        
        response = await client.request(
                request_method, final_url, headers=forwarded_headers, 
                content=request_body, cookies=request_cookies
        )
        # becasue probelm if reposne with status error will build an excpetion
        """  
        try:
            response = await client.request(
                request_method, final_url, headers=forwarded_headers, 
                content=request_body, cookies=request_cookies
            )
            print("\n\n========== RESPONSE DEBUG ==========\n", flush=True)
            print(f"🔗 Final URL: {final_url}", flush=True)
            print(f"🔄 Status Code: {response.status_code}", flush=True)
            print(f"📩 Headers:\n{response.headers}", flush=True)
            print("\n====================================\n", flush=True)
            response.raise_for_status()     
        except httpx.HTTPStatusError as exc:
            logger.error(f"❌ Request failed with status code {exc.response.status_code}")
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        except httpx.RequestError as exc:
            logger.error(f"❌ Request error: {exc}")
            raise HTTPException(status_code=500, detail="Internal Server Error") """
    """
    # Prepare response headers (excluding Set-Cookie) 
    response_headers = {
        key: value for key, value in response.headers.items() if key.lower() != "set-cookie"
    } 
    """
    response_headers = {
        key: value 
        for key, value in response.headers.items() 
        if key.lower() != "x-internal-token"
    }
    response_headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    # Set response content type
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
        media_type=content_type if content_type else None,
    ) 

# ====== 🏠 REDIRECT TO HOME 🏠 ======

@app.api_route("/", methods=["GET"])
async def redirect_to_home():
    """
    Redirect requests from '/' to '/home/'.
    """
    return RedirectResponse(url="/home/")

# ====== 🏆 Tournament Route Setup 🏆 ======

@app.api_route("/tournament/tournament-pattern/{tournament_id:int}/", methods=["GET"])
async def tournament_pattern_proxy(tournament_id, request: Request):
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

    # global user_id
    # user_id += 1

    is_auth, user_info = authentication.is_authenticated(request)

    if is_auth:
        user_id = user_info.get("user_id")
    else:
        user_id = 0

        # return RedirectResponse(url="/login/") # to FIX FLO

    print(
        "################## NEW USER CREATED #######################",
        user_id,
        flush=True,
    )
    print(path + str(user_id) + "/")

    if "HX-Request" in request.headers and "HX-Login-Success" not in request.headers:
        return await reverse_proxy_handler(
            "tournament", "tournament/" + path + str(user_id) + "/", request)
    elif path == "simple-match/": #to be replace by the proxy
        return await reverse_proxy_handler(
            "static_files", "/tournament-match-wrapper/" + str(user_id) + "/", request)
    elif path == "tournament/":
        return await reverse_proxy_handler(
            "static_files", "/tournament-wrapper/" + str(user_id) + "/", request)
    return await reverse_proxy_handler("static_files", "error/" + str(user_id) + "/", request)

# ====== ⚽ MATCH ROUTE ⚽ ======

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
async def match_proxy(path: str, request: Request, matchId: int = Query(None),
                    playerId: int = Query(None)
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
async def match_proxy(path: str, request: Request, matchId: int = Query(None),
                    playerId: int = Query(None)
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
        f"match/match2d/?matchId={matchId}&playerId={playerId}"
        if matchId is not None and playerId is not None
        else "match/"
    )

    return await reverse_proxy_handler("match", path, request)
    # reverse_proxy_request("static_files", "home", request)
    

# ====== 🚀 USER SERVICE ROUTE 🚀 ======

# WILL BE SUED INT EH FURTUR FOR THE FRIENDSHIP SYSTEM
@app.api_route("/user/{path:path}", methods=["GET"])
async def user_route(path: str, request: Request):

    # see if need to fix header hx login sucess
    if "HX-Request" in request.headers and "HX-Login-Success" not in request.headers:        
        return await reverse_proxy_handler("user", "/user/" + path, request)
    else:
        return await reverse_proxy_handler("user", "/user/" + path, request, 
            serve_from_static=True, static_service_name="static_files")

#OK
# handle the user account management
@app.api_route("/account/{path:path}", methods=["GET"])
async def user_account_route(path: str, request: Request):

    # see if need to fix header hx login sucess
    if "HX-Request" in request.headers and "HX-Login-Success" not in request.headers:        
        return await reverse_proxy_handler("user", "/account/" + path, request)
    else:
        return await reverse_proxy_handler("user", "/account/" + path, request, 
            serve_from_static=True, static_service_name="static_files")

@app.api_route("/auth/{path:path}", methods=["GET"])
async def user_auth_get_route(path:str, request: Request):
    
    # get will only be for login and register becaus e the resta re post
    print(f"\n == ROUTE AUTH WITH GET CALLED for path: {path} \n", flush=True)
    """   
    response = await auth_helpers.block_and_redir_auth_users()(request)
    if response:
        return response """
    if "HX-Request" in request.headers:
        return await reverse_proxy_handler("user", "/auth/" + path, request)
    else:
        return await reverse_proxy_handler("user", "/auth/" + path, request, 
            serve_from_static=True, static_service_name="static_files", is_full_page=True)

@app.api_route("/auth/{path:path}", methods=["POST"])
async def user_auth_post_route(path:str, request: Request):

    print(f"\n == CALLED AUTH ROUTE POSTE for path {path} == \n", flush=True)
    response = await reverse_proxy_handler("user", "/auth/" + path, request)
    if path == "login/":
        try:
            return await cookies_helpers.set_auth_cookies(response)  # Call cookie helper
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error setting login cookies: {str(e)}")
    elif path == "logout/":
        try:
            print("\n\n == LOGOUT AUTH ROUTE POST CALLED == \n\n", flush=True)
            return await cookies_helpers.clear_auth_cookies(response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error clearing authentication cookies: {str(e)}") 
    else:
        return HTTPException(status_code=404, detail="Path not found")


# ====== 🗂️ API DATABASE PROXY 🗂️ ======

@app.api_route("/api-database/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def databaseapi_proxy(path: str, request: Request):
    
    """
    Proxy requests to the database API microservice.

    - **path**: The path to the resource in the database API

    ### GET Examples:
    - **List all players**: GET /api-database/player/
    - **Get player by ID**: GET /api-database/player/1/
    - **Filter players by username**: GET /api-database/player/?username=player1
    - **Filter players by email**: GET /api-database/player/?email=example

    - **List all tournaments**: GET /api-database/tournament/
    - **Get tournament by ID**: GET /api-database/tournament/1/

    - **List all matches**: GET /api-database/match/
    - **Get match by ID**: GET /api-database/match/1/
    - **Filter matches by player**: GET /api-database/match/?player1=1
    - **Filter matches by tournament**: GET /api-database/match/?tournament=1

    ### POST Examples:
    - **Create a new player**: POST /api-database/player/
    - **Create a new tournament**: POST /api-database/tournament/
    - **Create a new match**: POST /api-database/match/

    ### Pagination:
    - All list endpoints are paginated with 10 items per page
    - **Navigate pages**: GET /api-database/player/?page=2

    ### Check 2FA:
    - **Check 2FA**: POST /api-database/check-2fa/
    - **Body**:
      - `username`: The username of the user
      - `password`: The password of the user
    - **Responses**:
      - `200 OK`: The user is authenticated and 2FA is not enabled
      - `401 Unauthorized`: The user is authenticated but 2FA is enabled

    ### Response format:
    ```json
    {
        "count": 100,
        "next": "http://localhost:8005/api-database/player/?page=2",
        "previous": null,
        "results": [
            {
                "id": 1,
                "username": "player1",
                "email": "player1@example.com",
                ...
            },
            ...
        ]
    }
    ```
    """
    return await reverse_proxy_handler("databaseapi", f"api/{path}", request)

# -----------------------------------------------------------
# MODIFY TO AHDNLE IN USER MANAGEMENT

""" @app.api_route("/login/{path:path}", methods=["GET"])
@app.api_route("/login", methods=["GET"])
async def login_page_route(request: Request, path: str = ""):

    Proxy for serving the login page.
    Redirects to home if user is already authenticated.

    # Check if user is authenticated
    response = refresh_access_token_and_redirect(request)
    if response:
        return respons
    # If not authenticated, show login page
    return await reverse_proxy_handler("static_files", "login/", request) """

# Add auth-status endpoint for debugging
""" @app.get("/auth/status")
async def auth_status(request: Request):
    Returns current authentication status - useful for debugging
    is_auth, user_info = is_authenticated(request)

    # Log the cookies for debugging
    print(f"🍪 Status check cookies: {request.cookies}", flush=True)

    # Create the response
    response = JSONResponse(
        {
            "authenticated": is_auth,
            "user": user_info,
            "cookies": {
                "has_access_token": "access_token" in request.cookies,
                "has_refresh_token": "refresh_token" in request.cookies,
            },
        },
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "X-Content-Type-Options": "nosniff",
        },
    )

    # If token refresh is needed, set the new access token cookie
    if is_auth and user_info and user_info.get("refresh_needed"):
        print("🔄 Setting refreshed access token in response", flush=True)
        response.set_cookie(
            key="access_token",
            value=user_info.get("new_access_token"),
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 6,  # 6 hours
        )

    return response """


""" @app.api_route("/register/{path:path}", methods=["GET"])
@app.api_route("/register", methods=["GET"])
async def register_page_route(request: Request, path: str = ""):
    Proxy for serving the register page.
    Redirects to home if user is already authenticated.
    # Check if user is authenticated
    is_auth, user_info = is_authenticated(request)

    if is_auth:
        # If authenticated, redirect to home
        response = RedirectResponse(url="/home")

        # If token refresh is needed, set the new access token cookie
        if user_info and user_info.get("refresh_needed"):
            print("🔄 Setting refreshed access token during login redirect", flush=True)
            response.set_cookie(
                key="access_token",
                value=user_info.get("new_access_token"),
                httponly=True,
                secure=True,
                samesite="Lax",
                path="/",
                max_age=60 * 60 * 6,  # 6 hours
            )

        return response

    # If not authenticated, show login page
    return await reverse_proxy_handler("static_files", "register/", request)
 """

""" @app.api_route("/auth/register", methods=["POST"])
@app.api_route("/auth/register/", methods=["POST"])
async def register_page_route(request: Request):
    Extracts form data and passes it to `register_fastAPI`
    form_data = await request.form()  # Extract form data

    first_name = form_data.get("first_name")
    last_name = form_data.get("last_name")
    username = form_data.get("username")
    password = form_data.get("password")
    email = form_data.get("email")
    # Create a new response object
    response = Response()

    return await register_fastAPI(
        request, response, username, password, email, first_name, last_name
    )

 """


@app.api_route("/two-factor-auth/", methods=["GET"])
async def two_factor_auth_proxy(request: Request):
    """
    Proxy requests to the two-factor authentication page.
    """
    print("🔐 Handling two-factor-auth request", flush=True)
    print(f"🔐 Headers: {request.headers}", flush=True)
    print(f"🔐 Cookies: {request.cookies}", flush=True)

    # Check if this is an HTMX request
    is_htmx = "HX-Request" in request.headers
    print(f"🔐 Is HTMX request: {is_htmx}", flush=True)

    # If we have a username in the query parameters, make sure it's passed to the template
    query_params = request.query_params
    username = query_params.get("username")
    if username:
        print(f"🔐 Username from query params: {username}", flush=True)
        # You might want to append it to the URL that's being proxied
        return await reverse_proxy_handler(
            "static_files", f"two-factor-auth/?username={username}", request
        )

    # Forward the request to the static_files service
    return await reverse_proxy_handler("static_files", "two-factor-auth/", request)


@app.api_route("/user/setup-2fa/", methods=["GET"])
@app.api_route("/setup-2fa/", methods=["GET"])
async def setup_2fa_proxy(request: Request):
    """
    Proxy requests for 2FA setup to the user microservice.
    """
    print("🔐 Handling setup-2fa request", flush=True)
    print(f"🔐 Headers: {request.headers}", flush=True)

    return await reverse_proxy_handler("user", "user/setup-2fa/", request)


@app.api_route("/user/verify-2fa/", methods=["POST"])
@app.api_route("/verify-2fa/", methods=["POST"])
async def verify_2fa_proxy(request: Request):
    """
    Proxy requests for 2FA verification to the user microservice.
    """
    print("🔐 Handling verify-2fa request", flush=True)
    print(f"🔐 Headers: {request.headers}", flush=True)

    return await reverse_proxy_handler("user", "user/verify-2fa/", request)


@app.api_route("/auth/verify-2fa/", methods=["POST"])
async def verify_2fa_login(request: Request):
    """
    Verifies 2FA code during login and generates JWT tokens if valid
    """
    print("🔐 Processing 2FA verification during login", flush=True)

    # Get the form data
    form_data = await request.form()
    print(f"🔐 Form data: {form_data}", flush=True)

    token = form_data.get("token")
    username = form_data.get("username")

    print(f"🔐 Extracted from form - username: {username}, token: {token}", flush=True)

    # Create a new response object
    response = Response()

    # Process the 2FA verification and generate JWT
    from authentication import verify_2fa_and_login

    return await verify_2fa_and_login(request, response, username, token)


# ! HO LA CONG DE SA MERE LA ROUTE APIIIIIIIIIIIIIIIIIIIIIIIIIII
@app.api_route("/user/disable-2fa/", methods=["GET", "POST"])
@app.api_route("/disable-2fa/", methods=["GET", "POST"])
async def disable_2fa_proxy(request: Request):
    """
    Proxy requests for 2FA disabling to the user microservice.
    """
    print("🔐 Handling disable-2fa request", flush=True)
    print(f"🔐 Headers: {request.headers}", flush=True)

    return await reverse_proxy_handler("user", "user/disable-2fa/", request)


@app.api_route("/user/delete-profile/", methods=["GET", "POST"])
@app.api_route("/delete-profile/", methods=["GET", "POST"])
async def delete_profile_proxy(request: Request):
    """
    Proxy requests for profile deletion to the user microservice.
    """
    print("🗑️ Handling delete-profile request", flush=True)
    print(f"🗑️ Method: {request.method}", flush=True)

    # Log headers for debugging CSRF issues
    print(f"🗑️ Headers: {request.headers}", flush=True)

    # For GET requests, make sure we get a fresh CSRF token
    if request.method == "GET":
        response = await reverse_proxy_handler("user", "user/delete-profile/", request)
        # Ensure Set-Cookie headers are preserved
        return response

    # Forward the request to the user microservice
    response = await reverse_proxy_handler("user", "user/delete-profile/", request)

    # If it's a POST request and deletion was successful, clear JWT cookies
    if request.method == "POST" and response.status_code == 200:
        try:
            # Parse the response content to check for success
            content = json.loads(response.body.decode())
            if content.get("success"):
                print("🗑️ Profile deletion successful, clearing cookies", flush=True)

                # Clear the cookies
                response.delete_cookie(key="access_token", path="/")
                response.delete_cookie(key="refresh_token", path="/")

                # Set HX-Redirect header for client-side redirection
                response.headers["HX-Redirect"] = "/register/"

                print("🗑️ Cookies cleared and redirect set", flush=True)
        except Exception as e:
            print(f"🗑️ Error processing deletion response: {str(e)}", flush=True)

    return response


@app.api_route("/user/delete-profile/", methods=["GET", "POST"])
@app.api_route("/delete-profile/", methods=["GET", "POST"])
async def delete_profile_proxy(request: Request):
    """
    Proxy requests for profile deletion to the user microservice.
    """
    print("🗑️ Handling delete-profile request", flush=True)
    print(f"🗑️ Method: {request.method}", flush=True)

    # Log headers for debugging CSRF issues
    print(f"🗑️ Headers: {request.headers}", flush=True)

    # For GET requests, make sure we get a fresh CSRF token
    if request.method == "GET":
        response = await reverse_proxy_handler("user", "user/delete-profile/", request)
        # Ensure Set-Cookie headers are preserved
        return response

    # Forward the request to the user microservice
    response = await reverse_proxy_handler("user", "user/delete-profile/", request)

    # If it's a POST request and deletion was successful, clear JWT cookies
    if request.method == "POST" and response.status_code == 200:
        try:
            # Parse the response content to check for success
            content = json.loads(response.body.decode())
            if content.get("success"):
                print("🗑️ Profile deletion successful, clearing cookies", flush=True)

                # Clear the cookies
                response.delete_cookie(key="access_token", path="/")
                response.delete_cookie(key="refresh_token", path="/")

                # Set HX-Redirect header for client-side redirection
                response.headers["HX-Redirect"] = "/register/"

                print("🗑️ Cookies cleared and redirect set", flush=True)
        except Exception as e:
            print(f"🗑️ Error processing deletion response: {str(e)}", flush=True)

    return response


# ---------------------------------------------------------------


@app.api_route("/{path:path}", methods=["GET"])
async def static_files_proxy(path: str, request: Request):
    """
    Proxy requests to the static files microservice.

    THE SPA'S INDEX.HTML FILE IS HERE!!!

    - **path**: The path to the resource in the static files service.
    - **request**: The incoming request object.
    """
    # ! UNCOMMENT THOSE LINES TO LOCK THE WEBSITE IF NOT AUTHENTICATED
    # is_auth, user_info = is_authenticated(request)

    # if is_auth == False:
    #     # If not authenticated, redirect to register
    #     response = RedirectResponse(url="/register/")

    #     return response
    # ! UNCOMMENT THOSE LINES TO LOCK THE WEBSITE IF NOT AUTHENTICATED

    return await reverse_proxy_handler("static_files", path, request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)


# ---------------- Others 

# @app.websocket("/ws/tournament/")
# async def tournament_websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             print("message received: {data}")
#             await websocket.send_text(f"Message text was: {data}")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         await websocket.close()

# @app.websocket("/ws/match/")
# async def match_websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             print("message received: {data}")
#             await websocket.send_text(f"Message text was: {data}")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         await websocket.close()

# Probleme a regler:
# cliquer pour requete a "http://localhost:8000/tournament/simple-match/"
# ne passe pas par l'api_gateway!!!
# @app.api_route("/tournament/{path:path}",
# methods=["GET", "POST", "PUT", "DELETE"])
# async def tournament_proxy(path: str, request: Request):
#     return await reverse_proxy_request("tournament", "tournament/" + path, request)

# @app.api_route("/match/{path:path}",
# methods=["GET", "POST", "PUT", "DELETE"])
# async def match_proxy(path: str, request: Request):
#     return await reverse_proxy_request("match", "match/" + path, request)

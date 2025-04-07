from fastapi import FastAPI, Request, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import json


from authentication import (
    login_fastAPI,
    is_authenticated,
    logout_fastAPI,
    register_fastAPI,
)


app = FastAPI(
    title="API Gateway",
    description="This API Gateway routes requests to various microservices. \
        Define endpoints to get any data here :)",
    version="1.0.0",
)

# Configure CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=[
        "Content-Type",
        "X-CSRFToken",
        "Set-Cookie",
    ],  # Expose these headers
)


# error page handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return await proxy_request("static_files", f"error/{exc.status_code}/", request)


services = {
    "tournament": "http://tournament:8001",
    "match": "http://match:8002",
    "static_files": "http://static_files:8003",
    "user": "http://user:8004",
    "databaseapi": "http://databaseapi:8007",
}

# logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Exclude Path for the
AUTH_PATH = [
    "/login",
    "/register",
    "/login/",
    "/register/",
    "/auth/login/",
    "/auth/register/",
    "/two-factor-auth/",
    "/auth/verify-2fa/"
]

EXCLUDED_PATH = [
    "/favicon.ico",
    "/translations/de.json",
    "/translations/en.json",
    "/translations/es.json",
    "/translations/fr.json",
    "/translations/tl.json",
    "/match/stop-match/undefined/undefined/",
]

# TODO : To let error pages go through when non authenticated
# KNOWN_PATHS = [
#     "/login",

# ]



# ! NEED TO MIX THE BOUNCER LOGIC TO NON AUTH AND AUTH USERS
@app.middleware("http")
async def bouncer_middleware(request: Request, call_next):
    """
    Main Middleware to filter authenticated users from non-auth users
    """
    is_auth, user_info = is_authenticated(request)

    print(f"============= URL REQUEST ENTERING BOUNCER ================\n")
    print(f"=============           {request.url.path} ================\n")
    print(f"============= URL REQUEST ENTERING BOUNCER ================\n")

    # TODO : To let error pages go through when non authenticated
    # if request.url.path not in KNOWN_PATHS:
    #     print(f"👍 Bounder Middleware non trigered for error message on login/register pages 👍")
    #     response = await call_next(request)
    #     return response

    # Let go through the Middleware everyting included in EXCLUDED_PATH 
    if request.url.path in EXCLUDED_PATH:
        print(f"👍 Bounder Middleware non trigered 👍")
        response = await call_next(request)
        return response


    if is_auth and request.url.path in AUTH_PATH:
        print(f"⬅️ Auth user request auth pages, redirecting to home ⬅️")
        # Check if this is an HTMX request
        if "HX-Request" in request.headers:
            response = Response(status_code=200)
            response.headers["HX-Location"] = (
                "/home/"  # Use HX-Location for SPA navigation
            )
        else:
            response = RedirectResponse(url="/home/")
        return response

    elif not is_auth and request.url.path not in AUTH_PATH:
        print(f"⛔ Bounder Middleware Trigerred, non auth request ⛔")
        # Check if this is an HTMX request
        if "HX-Request" in request.headers:
            print(f"🔄 HTMX request detected, using HX-Location", flush=True)
            # HX-Location makes HTMX do a client-side redirect without a full page reload
            response = Response(status_code=200)
            response.headers["HX-Location"] = "/register/"
            # Clear JWT cookies
            response.delete_cookie(key="access_token", path="/")
            response.delete_cookie(key="refresh_token", path="/")
        else:
            print(f"🔄 Standard request, using RedirectResponse", flush=True)
            response = RedirectResponse(url="/register/")
            # Clear JWT cookies
            response.delete_cookie(key="access_token", path="/")
            response.delete_cookie(key="refresh_token", path="/")
        return response

    print(f"👍 Bounder Middleware non trigered 👍")
    
    response = await call_next(request)
    return response


# Token refresh middleware
@app.middleware("http")
async def jwt_refresh_middleware(request: Request, call_next):
    """
    Middleware that checks if the access token needs to be refreshed.
    If refresh is needed, it adds the new access token to the response.
    """
    # First process the request normally
    response = await call_next(request)

    # Check authentication status after request processing
    is_auth, user_info = is_authenticated(request)

    # If authenticated and token refresh needed, update the response cookies
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

    return response


# CSRF middleware
# @app.middleware("http")
# async def csrf_middleware(request: Request, call_next):
#     """
#     Middleware that verifies CSRF token for non-GET requests.
#     """
#     # Skip CSRF check for GET requests and health checks
#     if request.method == "GET" or request.url.path == "/health/":
#         return await call_next(request)

#     # Get CSRF token from cookie
#     csrf_token = request.cookies.get("csrf_token")

#     # Get CSRF token from header
#     header_token = request.headers.get("X-CSRFToken")

#     # Verify tokens match
#     if not csrf_token or not header_token or csrf_token != header_token:
#         return JSONResponse(
#             status_code=403,
#             content={"detail": "Invalid CSRF token"},
#         )

#     return await call_next(request)


# ! DEBUGGING COOKIES MIDDLEWARE, DO DELETE
# This middleware is used to debug incoming cookies in FastAPI.
# It prints the incoming cookies to the console.
@app.middleware("http")
async def debug_cookies_middleware(request: Request, call_next):
    print(f"🔍 Incoming Cookies in FastAPI: {request.cookies}", flush=True)
    response = await call_next(request)

    # Also log outgoing cookies in response headers
    if "set-cookie" in response.headers:
        print(
            f"🔍 Outgoing Set-Cookie headers: {response.headers.get('set-cookie')}",
            flush=True,
        )

    return response

async def proxy_request(service_name: str, path: str, request: Request):
    if service_name not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        base_url = services[service_name].rstrip("/")
        path = path.lstrip("/")
        url = f"{base_url}/{path}"

        print(
            "****************************\n",
            f"Proxying to: {url}",
            f"\nHX-Request header present: {'HX-Request' in request.headers}",
            f"\nRequest method: {request.method}",
            "\n****************************",
            flush=True,
        )

        # Forward all headers except 'host'
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in ["host"]
        }
        headers["Host"] = "localhost"

        # Check if user is authenticated and add user info to headers
        is_auth, user_info = is_authenticated(request)
        if is_auth and user_info:
            headers["X-User-ID"] = str(user_info.get("user_id", ""))
            headers["X-Username"] = user_info.get("username", "")

        # Log cookies for debugging
        print(f"🍪 Forwarding cookies: {request.cookies}", flush=True)

        method = request.method
        data = await request.body()
        cookies = request.cookies

        try:
            response = await client.request(
                method, url, headers=headers, content=data, cookies=cookies
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(f"Request failed with status code {exc.response.status_code}")
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.response.text
            )
        except httpx.RequestError as exc:
            logger.error(f"Request failed: {exc}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

        # Prepare response headers
        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in ["set-cookie"]
        }  # We'll handle cookies separately
        response_headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

        # Create the response object
        content_type = response.headers.get("Content-Type", "")

        # Create the FastAPI response
        fastapi_response = Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=content_type.split(";")[0].strip() if content_type else None,
        )

        return fastapi_response


@app.api_route("/tournament/tournament-pattern/{tournament_id:int}/", methods=["GET"])
async def tournament_pattern_proxy(tournament_id, request: Request):
    print("################## NEW ROUTE USED #######################", flush=True)
    print(f"################## NEW ROUTE USED ##########{tournament_id}", flush=True)
    return await proxy_request(
        "tournament", f"tournament/tournament-pattern/{tournament_id}/", request
    )


# user_id = 0


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

    is_auth, user_info = is_authenticated(request)

    if is_auth:
        user_id = user_info.get("user_id")
    else:
        user_id = 0

        # return RedirectResponse(url="/login/") # to FIX FLO
        # return RedirectResponse(url="/login/") # to FIX FLO

    print(
        "################## NEW USER CREATED #######################",
        user_id,
        flush=True,
    )
    print(path + str(user_id) + "/")

    if "HX-Request" in request.headers and "HX-Login-Success" not in request.headers:
        return await proxy_request(
            "tournament", "tournament/" + path + str(user_id) + "/", request
        )
    elif path == "simple-match/":
        return await proxy_request(
            "static_files", "/tournament-match-wrapper/" + str(user_id) + "/", request
        )
    elif path == "tournament/":
        return await proxy_request(
            "static_files", "/tournament-wrapper/" + str(user_id) + "/", request
        )
    else:
        error_message = "Page Not Found"

        return await proxy_request("static_files", "error/", request)


@app.api_route("/user/{path:path}", methods=["GET"])
async def user_proxy(path: str, request: Request):
    """
    Proxy requests to the user microservice.

    - **path**: The path to the resource in the user service.
    - **request**: The incoming request object.
    - **Headers**:
      - `HX-Request`: If present, the request is treated as an HTMX request.
    - **Responses**:
      - Returns the content from the user microservice.
      - If `path` is "profile/" or "stats/", returns specific content.
    """
    if "HX-Request" in request.headers and "HX-Login-Success" not in request.headers:
        return await proxy_request("user", "user/" + path, request)
    elif path == "profile/":
        return await proxy_request("static_files", "/user-profile-wrapper/", request)
    elif path == "stats/":
        return await proxy_request("static_files", "/user-stats-wrapper/", request)
    else:
        error_message = "Page Not Found"

        return await proxy_request("static_files", "error", request)


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
    return await proxy_request("match", "/match/stop-match/" + path, request)


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

    return await proxy_request("match", path, request)


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

    return await proxy_request("match", path, request)
    # elif path == "simple-match/":
    #     return await proxy_request("static_files", "/home/", request)


@app.get("/")
async def redirect_to_home():
    """
    Redirect requests from '/' to '/home/'.
    """
    return RedirectResponse(url="/home/")


# ! DATABASE API ROUTE
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
    return await proxy_request("databaseapi", f"api/{path}", request)


@app.api_route("/login/{path:path}", methods=["GET"])
@app.api_route("/login", methods=["GET"])
async def login_page_route(request: Request, path: str = ""):
    """
    Proxy for serving the login page.
    Redirects to home if user is already authenticated.
    """
    # Check if user is authenticated
    # is_auth, user_info = is_authenticated(request)

    # if is_auth:
    #     # If authenticated, redirect to home
    #     response = RedirectResponse(url="/home")

    # If token refresh is needed, set the new access token cookie
    # if user_info and user_info.get("refresh_needed"):
    #     print("🔄 Setting refreshed access token during login redirect", flush=True)
    #     response.set_cookie(
    #         key="access_token",
    #         value=user_info.get("new_access_token"),
    #         httponly=True,
    #         secure=True,
    #         samesite="Lax",
    #         path="/",
    #         max_age=60 * 60 * 6,  # 6 hours
    #     )

    # return response

    # If not authenticated, show login page
    return await proxy_request("static_files", "login/", request)


@app.api_route("/auth/login", methods=["POST"])
@app.api_route("/auth/login/", methods=["POST"])
async def login_page_route(request: Request):
    """
    Extracts form data and passes it to `login_fastAPI`
    """
    form_data = await request.form()  # Extract form data
    username = form_data.get("username")
    password = form_data.get("password")

    # Create a new response object
    response = Response()

    return await login_fastAPI(request, response, username, password)


# ! ROUTE TO DELETE
@app.get("/auth/status")
async def auth_status(request: Request):
    """
    Returns current authentication status - useful for debugging
    """
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

    return response


# Add logout endpoint
@app.api_route("/auth/logout", methods=["POST"])
@app.api_route("/auth/logout/", methods=["POST"])
async def logout_route(request: Request):
    """
    Handles user logout by clearing JWT cookies
    """
    return await logout_fastAPI(request)


@app.api_route("/register/{path:path}", methods=["GET"])
@app.api_route("/register", methods=["GET"])
async def register_page_route(request: Request, path: str = ""):
    """
    Proxy for serving the register page.
    Redirects to home if user is already authenticated.
    """
    # Check if user is authenticated
    # is_auth, user_info = is_authenticated(request)

    # if is_auth:
    #     # If authenticated, redirect to home
    #     response = RedirectResponse(url="/home")

    # If token refresh is needed, set the new access token cookie
    # if user_info and user_info.get("refresh_needed"):
    #     print("🔄 Setting refreshed access token during login redirect", flush=True)
    #     response.set_cookie(
    #         key="access_token",
    #         value=user_info.get("new_access_token"),
    #         httponly=True,
    #         secure=True,
    #         samesite="Lax",
    #         path="/",
    #         max_age=60 * 60 * 6,  # 6 hours
    #     )

    # return response

    # If not authenticated, show login page
    return await proxy_request("static_files", "register/", request)


@app.api_route("/auth/register", methods=["POST"])
@app.api_route("/auth/register/", methods=["POST"])
async def register_page_route(request: Request):
    """
    Extracts form data and passes it to `register_fastAPI`
    """
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
        return await proxy_request(
            "static_files", f"two-factor-auth/?username={username}", request
        )

    # Forward the request to the static_files service
    return await proxy_request("static_files", "two-factor-auth/", request)


@app.api_route("/user/setup-2fa/", methods=["GET"])
@app.api_route("/setup-2fa/", methods=["GET"])
async def setup_2fa_proxy(request: Request):
    """
    Proxy requests for 2FA setup to the user microservice.
    """
    print("🔐 Handling setup-2fa request", flush=True)
    print(f"🔐 Headers: {request.headers}", flush=True)

    return await proxy_request("user", "user/setup-2fa/", request)


@app.api_route("/user/verify-2fa/", methods=["POST"])
@app.api_route("/verify-2fa/", methods=["POST"])
async def verify_2fa_proxy(request: Request):
    """
    Proxy requests for 2FA verification to the user microservice.
    """
    print("🔐 Handling verify-2fa request", flush=True)
    print(f"🔐 Headers: {request.headers}", flush=True)

    return await proxy_request("user", "user/verify-2fa/", request)


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

    return await proxy_request("user", "user/disable-2fa/", request)


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
        response = await proxy_request("user", "user/delete-profile/", request)
        # Ensure Set-Cookie headers are preserved
        return response

    # Forward the request to the user microservice
    response = await proxy_request("user", "user/delete-profile/", request)

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

                # ! REDIRECT RELOAD THE SPA HERE
                response.headers["HX-Redirect"] = "/register/"
                # response = RedirectResponse(url="/register/")

                print("🗑️ Cookies cleared and redirect set", flush=True)
        except Exception as e:
            print(f"🗑️ Error processing deletion response: {str(e)}", flush=True)

    return response


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

    return await proxy_request("static_files", path, request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)

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
#     return await proxy_request("tournament", "tournament/" + path, request)

# @app.api_route("/match/{path:path}",
# methods=["GET", "POST", "PUT", "DELETE"])
# async def match_proxy(path: str, request: Request):
#     return await proxy_request("match", "match/" + path, request)

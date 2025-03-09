from fastapi import FastAPI, Request, HTTPException, Query
import httpx
from fastapi.responses import HTMLResponse, JSONResponse
import logging

app = FastAPI(
    title="API Gateway",
    description="This API Gateway routes requests to various microservices. \
        Define endpoints to get any data here :)",
    version="1.0.0",
)

services = {
    "tournament": "http://tournament:8001",
    "match": "http://match:8002",
    "static_files": "http://static_files:8003",
    "user": "http://user:8004",
    "authentication": "http://authentication:8006",
    "databaseapi": "http://databaseapi:8007",
}

# logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def proxy_request(service_name: str, path: str, request: Request):
    if service_name not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        base_url = services[service_name].rstrip("/")
        path = path.lstrip("/")
        url = f"{base_url}/{path}"

        print(
            "****************************\n",
            url,
            "\n****************************",
            flush=True,
        )
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in ["host"]
        }
        headers["Host"] = "localhost"

        method = request.method
        data = await request.body()

        try:
            response = await client.request(method, url, headers=headers, content=data)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error
            (f"Request failed with status code {exc.response.status_code}")
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.response.text
            )
        except httpx.RequestError as exc:
            logger.error(f"Request failed: {exc}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

        response_headers = {key: value for key, value in response.headers.items()}
        response_headers["Cache-Control"] = (
            "no-cache, \
            no-store, must-revalidate"
        )

        content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("text/html"):
            return HTMLResponse(content=response.text, status_code=response.status_code)
        return JSONResponse(content=response.json(), status_code=response.status_code)


user_id = 0


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

    global user_id
    user_id += 1
    print(
        "################## NEW USER CREATED #######################",
        user_id,
        flush=True,
    )
    print(path + str(user_id) + "/")

    if "HX-Request" in request.headers:
        return await proxy_request(
            "tournament", "tournament/" + path + str(user_id) + "/", request
        )
    elif path == "simple-match/":
        return await proxy_request(
            "static_files", "/tournament-match-wrapper/" + str(user_id) + "/", request
        )


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
    if "HX-Request" in request.headers:
        return await proxy_request("user", "user/" + path, request)
    elif path == "profile/":
        return await proxy_request("static_files", "/user-profile-wrapper/", request)
    elif path == "stats/":
        return await proxy_request("static_files", "/user-stats-wrapper/", request)


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


@app.api_route("/match/{path:path}", methods=["GET"])
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
        f"match/?matchId={matchId}&playerId={playerId}"
        if matchId is not None and playerId is not None
        else "match/"
    )

    return await proxy_request("match", path, request)
    # elif path == "simple-match/":
    #     return await proxy_request("static_files", "/home/", request)


@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def authentication_proxy(path: str, request: Request):
    """
    Proxy requests to the authentication microservice.
    """
    return await proxy_request("authentication", f"auth/{path}", request)


@app.api_route("/api/{path:path}", methods=["GET"])
async def databaseapi_proxy(path: str, request: Request):
    """
    Proxy requests to the database API microservice.

    - **path**: The path to the resource in the database API

    ### Examples:
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
    """
    return await proxy_request("databaseapi", f"api/{path}", request)


@app.api_route("/api/{path:path}", methods=["POST"])
async def databaseapi_proxy_post(path: str, request: Request):
    """
    Proxy POST requests to the database API microservice.

    - **path**: The path to the resource in the database API

    ### Examples:
    - **Register a new user**: POST /api/register/
    - **Verify credentials**: POST /api/verify-credentials/
    - **Refresh token**: POST /api/token/refresh/
    - **Verify token**: POST /api/token/verify/
    - **Enable 2FA**: POST /api/enable-2fa/
    - **Verify 2FA setup**: POST /api/verify-2fa-setup/
    """
    return await proxy_request("databaseapi", f"api/{path}", request)


@app.api_route("/api/{path:path}", methods=["PUT"])
async def databaseapi_proxy_put(path: str, request: Request):
    """
    Proxy PUT requests to the database API microservice.
    """
    return await proxy_request("databaseapi", f"api/{path}", request)


@app.api_route("/api/{path:path}", methods=["DELETE"])
async def databaseapi_proxy_delete(path: str, request: Request):
    """
    Proxy DELETE requests to the database API microservice.
    """
    return await proxy_request("databaseapi", f"api/{path}", request)


@app.api_route("/{path:path}", methods=["GET"])
async def static_files_proxy(path: str, request: Request):
    """
    Proxy requests to the static files microservice.

    THE SPA'S INDEX.HTML FILE IS HERE!!!

    - **path**: The path to the resource in the static files service.
    - **request**: The incoming request object.
    """
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

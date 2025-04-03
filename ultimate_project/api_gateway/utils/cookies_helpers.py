from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
import json

async def set_auth_cookies(response):
    # Validate response is not None
    if response.status_code >= 400:
        return response 
    if response is None:
        raise HTTPException(status_code=400, detail="Response object is missing")
    # Ensure response has a body
    if not hasattr(response, "body") or response.body is None:
        raise HTTPException(status_code=400, detail="Response body is missing")
    # Decode the response body to string
    try:
        response_text = response.body.decode('utf-8').strip()
        if not response_text:
            raise HTTPException(status_code=400, detail="Response body is empty")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode response body: {str(e)}")

    # Try parsing the JSON response
    try:
        response_data = json.loads(response_text)  # Extract JSON correctly
        print(f"Response Data: {response_data}", flush=True)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Response body is not valid JSON")

    # Extract access_token and refresh_token
    access_token = response_data.get("access_token")
    refresh_token = response_data.get("refresh_token")

    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="Access token and refresh token are required")

    # Process cookies if tokens are present
    print("Tokens received, setting cookies...")

    content = {"success": True, "message": "Auth cookies were created successfully."}

    # Create response object to set cookies
    response = JSONResponse(content=content, status_code=200)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        path="/",
        max_age=60 * 60 * 6  # 6 hours
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        path="/",
        max_age=60 * 60 * 24 * 7  # 7 days
    )

    print("🔑 COOKIES SET SUCCESSFULLY", flush=True)
    return response


async def clear_auth_cookies(response: Response):
    """
    Clears authentication cookies (access_token and refresh_token) from the response.
    This will set the cookies' max_age to 0 and expires to a past date, effectively deleting them.
    """
    response = JSONResponse(content={"success": True, "message": "Déconnexion réussie"})
    # Clear cookies by setting them with empty values and making them expire immediately
    response.delete_cookie(
        key="access_token",
        path="/",  # Must match how it was set
        httponly=True,  # Must match how it was set
        samesite="Lax",  # Must match how it was set
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",  # Must match how it was set
        httponly=True,  # Must match how it was set
        samesite="Lax",  # Must match how it was set
    )

    # Add a header for HTMX to redirect to login page
    response.headers["HX-Location"] = "/auth/login/"
    # Log for debugging
    print("🔑 JWT Cookies cleared", flush=True)
    return response
    

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import requests
import jwt
import datetime
import os
import pyotp
import re
import secrets
import hashlib
import urllib.parse


async def set_login_cookies(body: dict):
    """
    This function accepts a body conataining an access token and refresh token, 
    then sets them as cookiesin the response object.
    """
    access_token = body.get("access_token")
    refresh_token = body.get("refresh_token")
    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="access_token and refresh_token are required")
    # Create Response object to set cookies
    response = Response(content="Cookies set successfully!", status_code=200)
    response.set_cookie(
        key="access_token",
        value=access_token,
        path="/",
        max_age=60 * 60 * 6,  # Example: 6 hours
        secure=True,
        httponly=True,
        samesite="None"
    )
    # Set the refresh_token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        path="/",
        max_age=60 * 60 * 24 * 7,  # Example: 7 days
        secure=True,
        httponly=True,
        samesite="None"
    )
    print(f"🔑 COOKIES CRETAED INS ET LOGIN COOKIES", flush=True)
    return (response)

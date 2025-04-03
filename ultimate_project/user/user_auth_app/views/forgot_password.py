from django.shortcuts import render
import json
import os
from itsdangerous import URLSafeTimedSerializer
from django.http import HttpRequest, JsonResponse
from utils import utils_user_auth


INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN")

async def forgot_password_view(request: HttpRequest):
    
    if request.method == 'GET':
        csrf_token = request.COOKIES.get('csrftoken')
        response = render(request,"forgot-password.html", {"csrftoken": csrf_token})
        response["X-Page-Name"] = "forgot-password.html"
        return response
    
    if request.method == 'POST':
        # Create a new response object
        response =  await utils_user_auth.register_handler(request)
        if isinstance(response, JsonResponse):
            try:
                data = json.loads(response.content.decode())  # Decode bytes and load JSON
                new_response = JsonResponse(data, status=response.status_code)
                new_response.setdefault("X-Internal-Token", INTERNAL_TOKEN)  
                return new_response  # Return the modified response
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON response"}, status=500)

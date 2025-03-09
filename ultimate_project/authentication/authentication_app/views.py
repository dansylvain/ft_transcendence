import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Call the database API to verify credentials
        try:
            response = requests.post(
                'http://databaseapi:8007/api/verify-credentials/',
                data={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                # Authentication successful
                auth_data = response.json()
                
                # Store user info in session (not the tokens)
                request.session['user_id'] = auth_data['user_id']
                request.session['username'] = auth_data['username']
                
                # Create the response for redirect
                response = redirect('home')
                
                # Set JWT tokens in HTTP-only cookies
                response.set_cookie(
                    'access_token',
                    auth_data['access_token'],
                    httponly=True,              # Not accessible via JavaScript
                    secure=True,                # Sent only over HTTPS
                    samesite='Lax',             # CSRF protection
                    max_age=60*60               # 1 hour (match your JWT settings)
                )
                
                response.set_cookie(
                    'refresh_token',
                    auth_data['refresh_token'],
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    max_age=60*60*24            # 1 day (match your JWT settings)
                )
                
                return response
                
                # Redirect to home or dashboard
                return redirect('home')
            else:
                # Authentication failed
                error_message = response.json().get('error', 'Authentication failed')
                messages.error(request, error_message)
        except requests.exceptions.RequestException as e:
            # Handle connection errors
            messages.error(request, f"Connection error: {str(e)}")
    
    # For GET requests or failed POST, show the login form
    return render(request, 'authentication_app/login.html')
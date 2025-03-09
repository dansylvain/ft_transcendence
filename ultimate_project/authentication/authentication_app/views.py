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
            
                # Store JWT tokens in session or cookies
                request.session['access_token'] = auth_data['access_token']
                request.session['refresh_token'] = auth_data['refresh_token']
                request.session['user_id'] = auth_data['user_id']
                request.session['username'] = auth_data['username']
                
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
curl -i -s -X POST http://databaseapi:8007/api-database/verify-credentials/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1", "password":"password"}'









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
                'http://databaseapi:8000/api-database/verify-credentials/',
                data={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                # Authentication successful
                auth_data = response.json()
                
                # Store auth token in session or cookie
                request.session['auth_token'] = auth_data['token']
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




	
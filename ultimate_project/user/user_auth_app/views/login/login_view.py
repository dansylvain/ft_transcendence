# from django.views.decorators.http import require_POST
from django.shortcuts import render
# from django.http import HttpResponseBadRequest
from django.http import HttpRequest, JsonResponse

from utils import utils_user_auth

async def login_view(request: HttpRequest):
    """
    Extracts form data and passes it to `login_fastAPI`
    """

    print("\n===========\nLOGIN VIEW CALLED\n===========\n", flush=True)
    
    if request.method == 'GET':
        print("\n===========\nLOGIN VIEW RECEIVED THE GET\n===========\n", flush=True)
        # i ened to do an api requets to check if a user is alredy
        # login like simeute the is auth fucntion
        return render(request, "login.html")
        
    if request.method == 'POST':
        form_data = await request.form()  # Extract form data
        username = form_data.get("username")
        password = form_data.get("password")
        return await (utils_user_auth.login_api(username, password))
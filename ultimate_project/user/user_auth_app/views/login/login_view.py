from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.http import HttpRequest, JsonResponse

from utils import user_auth


async def login_view(request: HttpRequest):
    """
    Extracts form data and passes it to `login_fastAPI`
    """
    #if request.method == 'GET':
        # i ened to do an api requets to check if a user is alredy
        # login like simeute the is auth fucntion
        
    if request.method == 'POST':
        form_data = await request.form()  # Extract form data
        username = form_data.get("username")
        password = form_data.get("password")

        return await (user_auth.login_api(username, password))
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

#csutom view for specific information avoid getting 

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_credentials(request):
    """
    Verify username and password without creating a session.
    Returns user info and token on success.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    # print("=========== DEBUGGING DATABASE===========", flush=True)
    # print(f"username: {username}, password: {password}", flush=True)
    # print("=========== DEBUGGING DATABASE===========", flush=True)

    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Authententicate the user within the database system
    # ! IMPORTANT : Authenticate does not login the user 
    user = authenticate(username=username, password=password)

    if user:
        return Response(
            {
                "success": True, # returs a 200 code
                # returning extra info, see if pertinent in the login workflow
                "user_id": user.id,
                "username": user.first_name,
            }
        )
    else:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )
    
@api_view(["POST"])
@permission_classes([AllowAny])
def check_2fa(request):
    """
    Check if 2FA is enabled for a user.
    """
    
    print("\n\n == check2FA called == \n\n", flush=True)
    
    username = request.data.get("username")
    password = request.data.get("password")

    # Verify credentials
    user = authenticate(username=username, password=password)
    if not user:
        print("\n\n == INVALID CREDENTIALS == \n\n", flush=True)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if 2FA is enabled
    if not user.two_fa_enabled:
        print("\n\n == 2FA IS NOT ENABLED == \n\n", flush=True)
        return Response({"success": False, "message": "2FA is not enabled"}, status=status.HTTP_200_OK)
    return Response({"success": True}, status=status.HTTP_200_OK)

# ! POTENTIALLY OLD CLASS
@api_view(["POST"])
@permission_classes([AllowAny])
def check_2fa_code(request):
    """
    Check if a 2FA code is valid for a user.
    """
    username = request.data.get("username")
    code = request.data.get("code")

    # Check if 2FA is enabled
    user = authenticate(username=username, password=password) # type: ignore
    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if the code is valid
    if not user.two_fa_enabled:
        return Response({"error": "2FA is not enabled"}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({"success": True}, status=status.HTTP_200_OK)

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
    if not request.content_type or "application/json" not in request.content_type:
        return Response(
            {"success": False, "error": "Invalid content type. Expected application/json."},
            status=status.HTTP_400_BAD_REQUEST,
            content_type="application/json",
        )

    try:
        request_data = request.data
        if not isinstance(request_data, dict):
            raise ValueError("Request data must be a valid JSON object")
        username = request_data.get("username")
        password = request_data.get("password")

        if not username or not password:
            return Response(
                {"success": False, "error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        user = authenticate(username=username, password=password)
        if user is not None:
            return Response(
                {
                    "success": True,
                    "user_id": user.id,
                    "username": user.first_name,
                },
                status=status.HTTP_200_OK,
                content_type="application/json",
            )
        else:
            return Response(
                {"success": False, "error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
                content_type="application/json",
            )
    except ValueError as ve:
        return Response(
            {"success": False, "error": str(ve)},
            status=status.HTTP_400_BAD_REQUEST,
            content_type="application/json",
        )
    except Exception as e:
        return Response(
            {"success": False, "error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content_type="application/json",
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

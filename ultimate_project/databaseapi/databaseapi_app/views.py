from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.utils import timezone
from .models import Player


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
                "success": True,  # returs a 200 code
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
    username = request.data.get("username")
    password = request.data.get("password")

    # Verify credentials
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if 2FA is enabled
    if not user.two_fa_enabled:
        return Response(
            {"error": "2FA is not enabled"}, status=status.HTTP_401_UNAUTHORIZED
        )

    return Response({"success": True}, status=status.HTTP_200_OK)


# ! POTENTIALLY OLD CLASS, DO DELETE WITHIN TESTS
@api_view(["POST"])
@permission_classes([AllowAny])
def check_2fa_code(request):
    """
    Check if a 2FA code is valid for a user.
    """
    username = request.data.get("username")
    code = request.data.get("code")

    # Check if 2FA is enabled
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if the code is valid
    if not user.two_fa_enabled:
        return Response(
            {"error": "2FA is not enabled"}, status=status.HTTP_401_UNAUTHORIZED
        )

    return Response({"success": True}, status=status.HTTP_200_OK)


@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def uuid(request, player_id):
    """
    Handle GET and PUT requests for a player's session UUID
    GET: Retrieve the current session UUID
    PUT: Update the session UUID
    """
    try:
        player = Player.objects.get(id=player_id)

        if request.method == "GET":
            # Return the current UUID
            return JsonResponse(
                {
                    "uuid": str(player.uuid),
                }
            )

        elif request.method == "PUT":
            # Update the player's UUID from request body
            import json

            data = json.loads(request.body)
            new_uuid = data.get("uuid")

            if not new_uuid:
                return JsonResponse({"error": "uuid is required"}, status=400)

            # Store previous UUID if needed for handling disconnects
            previous_uuid = str(player.uuid) if player.uuid else None

            # Update the session information
            player.uuid = new_uuid
            player.save(update_fields=["uuid"])

            return JsonResponse({"success": True, "previous_uuid": previous_uuid})

    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)

    # If method not supported
    return JsonResponse({"error": "Method not allowed"}, status=405)

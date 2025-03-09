from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Player


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_credentials(request):
    username = request.data.get("username")
    password = request.data.get("password")
    otp_code = request.data.get("otp_code")  # For 2FA

    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user:
        # Check if 2FA is enabled
        if user.two_fa_enabled:
            # If 2FA is enabled but no OTP code provided, return 2FA required
            if not otp_code:
                return Response(
                    {
                        "two_fa_required": True,
                        "user_id": user.id,
                        "username": user.username,
                    },
                    status=status.HTTP_200_OK,
                )

            # Verify OTP code
            import pyotp

            totp = pyotp.TOTP(user.two_fa_secret)
            if not totp.verify(otp_code):
                return Response(
                    {"error": "Invalid 2FA code"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "two_fa_enabled": user.two_fa_enabled,
            }
        )
    else:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    enable_2fa = request.data.get("enable_2fa", False)

    # Convert string 'True'/'False' to boolean if needed
    if isinstance(enable_2fa, str):
        enable_2fa = enable_2fa.lower() == "true"

    # Validate input
    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if username already exists
    if Player.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if email already exists (if provided)
    if email and Player.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Create new user
        user = Player.objects.create_user(
            username=username, email=email, password=password
        )

        # Set 2FA if enabled
        if enable_2fa:
            import pyotp

            user.two_fa_enabled = True
            user.two_fa_secret = pyotp.random_base32()  # Generate a random secret
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "two_fa_enabled": user.two_fa_enabled,
                "two_fa_secret": user.two_fa_secret if user.two_fa_enabled else None,
            },
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response(
            {"error": "Please provide a refresh token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        refresh = RefreshToken(refresh_token)

        return Response(
            {
                "access": str(refresh.access_token),
            }
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_token(request):
    token = request.data.get("token")

    if not token:
        return Response(
            {"error": "Please provide a token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from rest_framework_simplejwt.tokens import AccessToken

        # This will raise an exception if the token is invalid
        token_obj = AccessToken(token)
        payload = token_obj.payload

        return Response(payload)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def user_from_token(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(
            {"error": "Authorization header missing or invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = auth_header.split(" ")[1]

    try:
        from rest_framework_simplejwt.tokens import AccessToken

        # This will raise an exception if the token is invalid
        token_obj = AccessToken(token)
        payload = token_obj.payload

        # Get the user ID from the token payload
        user_id = payload.get("user_id")

        if not user_id:
            return Response(
                {"error": "Invalid token payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the user from the database
        try:
            user = Player.objects.get(id=user_id)

            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_active": user.is_active,
                    "two_fa_enabled": user.two_fa_enabled,
                }
            )
        except Player.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
def enable_2fa(request):
    """Enable 2FA for the authenticated user."""
    # Get the user from the token
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(
            {"error": "Authorization header missing or invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = auth_header.split(" ")[1]

    try:
        from rest_framework_simplejwt.tokens import AccessToken

        # This will raise an exception if the token is invalid
        token_obj = AccessToken(token)
        payload = token_obj.payload

        # Get the user ID from the token payload
        user_id = payload.get("user_id")

        if not user_id:
            return Response(
                {"error": "Invalid token payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the user from the database
        try:
            user = Player.objects.get(id=user_id)

            # Generate a new 2FA secret
            import pyotp
            import qrcode
            import base64
            from io import BytesIO

            # Generate a random secret
            secret = pyotp.random_base32()

            # Create a QR code
            totp = pyotp.TOTP(secret)
            uri = totp.provisioning_uri(user.username, issuer_name="Transcendence")

            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convert image to base64 for embedding in HTML
            buffered = BytesIO()
            img.save(buffered)
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Store the secret temporarily (not verified yet)
            user.two_fa_secret = secret
            user.save()

            return Response(
                {
                    "secret": secret,
                    "qr_code_url": f"data:image/png;base64,{img_str}",
                }
            )
        except Player.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
def verify_2fa_setup(request):
    """Verify the 2FA setup and enable it for the user."""
    # Get the user from the token
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(
            {"error": "Authorization header missing or invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = auth_header.split(" ")[1]
    otp_code = request.data.get("otp_code")

    if not otp_code:
        return Response(
            {"error": "Please provide an OTP code"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from rest_framework_simplejwt.tokens import AccessToken

        # This will raise an exception if the token is invalid
        token_obj = AccessToken(token)
        payload = token_obj.payload

        # Get the user ID from the token payload
        user_id = payload.get("user_id")

        if not user_id:
            return Response(
                {"error": "Invalid token payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the user from the database
        try:
            user = Player.objects.get(id=user_id)

            # Verify the OTP code
            import pyotp

            totp = pyotp.TOTP(user.two_fa_secret)
            if totp.verify(otp_code):
                # Enable 2FA for the user
                user.two_fa_enabled = True
                user.two_fa_verified = True
                user.save()

                return Response({"success": True})
            else:
                return Response(
                    {"error": "Invalid OTP code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Player.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_401_UNAUTHORIZED,
        )

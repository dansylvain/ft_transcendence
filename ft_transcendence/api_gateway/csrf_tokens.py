import secrets

def csrf_validator(request):

    csrftoken = request.cookies.get("csrftoken")

    if not csrftoken:
        print("❌ CSRF token not found ❌", flush=True)
        return False
    elif not validate_csrf_token(csrftoken):
        print("❌ CSRF token is invalid ❌", flush=True)
        return False

    # print("✅ CSRF token is valid ✅", flush=True)
    return True


def generate_csrf_token():
    token = secrets.token_hex(16)
    return token


def validate_csrf_token(token):
    if not token:
        return False

    try:
        # Check if token is a valid hex string of the right length
        if len(token) == 32 and all(c in "0123456789abcdef" for c in token.lower()):
            return True
        else:
            print(f"Invalid token format: {token[:10]}...")
            return False
    except Exception as e:
        print(f"CSRF validation error: {e}", flush=True)
        return False
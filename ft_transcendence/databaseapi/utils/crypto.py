from cryptography.fernet import Fernet
from django.conf import settings

# Get the key from settings
FERNET_KEY = getattr(settings, "FERNET_SECRET_KEY", None)

if not FERNET_KEY:
    raise ValueError("FERNET_SECRET_KEY is missing from settings!")

cipher = Fernet(FERNET_KEY.encode())


# Encrypts the 2FA secret key
def encrypt_2fa_secret(secret):
    return cipher.encrypt(secret.encode()).decode()


# Decrypts the 2FA secret key
def decrypt_2fa_secret(encrypted_secret):
    return cipher.decrypt(encrypted_secret.encode()).decode()

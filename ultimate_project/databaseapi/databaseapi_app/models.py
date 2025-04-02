import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from utils.crypto import encrypt_2fa_secret, decrypt_2fa_secret


class PlayerManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hash the password before saving
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(username, email, password, **extra_fields)


#  ================= MODELS MANAGED BY THIS MICROSERVICE (user) =================
class Player(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, blank=True)

    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # needed for admin access

    # 2FA fields
    two_fa_enabled = models.BooleanField(default=False)  # 2FA toggle
    _two_fa_secret = models.CharField(max_length=32, blank=True, null=True)

    # UUID field
    uuid = models.UUIDField(default=uuid.uuid4, blank=True)

    # Language field
    language = models.CharField(
        max_length=2,
        choices=[
            ("en", "English"),
            ("fr", "Francais"),
            ("de", "Deustch"),
            ("es", "Espanol"),
            ("tl", "TlhIngan"),
        ],
        default="en",
    )

    # Encrypt and decrypt 2FA secrets
    @property
    def two_fa_secret(self):
        return decrypt_2fa_secret(self._two_fa_secret) if self._two_fa_secret else None

    @two_fa_secret.setter
    def two_fa_secret(self, value):
        self._two_fa_secret = encrypt_2fa_secret(value) if value else None

    # Tells Django to use "email" as the primary field for authentication
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = PlayerManager()  # Custom manager

    class Meta:
        db_table = "player"  # Explicitly set the schema and table name

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Tournament(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = "tournament"

    def __str__(self):
        return f"Tournament {self.id}"


class Match(models.Model):
    id = models.AutoField(primary_key=True)

    player1 = models.ForeignKey(
        to=Player,  # Explicit reference to Player model
        on_delete=models.CASCADE,  # If a player is deleted, the match is also deleted
        related_name="player1",
    )
    player2 = models.ForeignKey(
        to=Player,
        on_delete=models.CASCADE,
        related_name="player2",
    )
    winner = models.ForeignKey(
        to=Player,
        on_delete=models.CASCADE,
        related_name="winner",
    )

    tournament = models.ForeignKey(
        to=Tournament,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "match"

    def __str__(self):
        return f"Match {self.id}"

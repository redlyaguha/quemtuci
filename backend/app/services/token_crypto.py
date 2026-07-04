"""Шифрование пользовательских токенов внешних интеграций [BE-M1]."""
from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def _fernet_key() -> bytes:
    if settings.token_encryption_key:
        return settings.token_encryption_key.encode()

    digest = hashlib.sha256(settings.jwt_secret_key.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_token(token: str) -> str:
    return Fernet(_fernet_key()).encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    return Fernet(_fernet_key()).decrypt(encrypted_token.encode()).decode()

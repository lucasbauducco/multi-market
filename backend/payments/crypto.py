"""Cifrado simétrico para guardar tokens de vendedores. La clave sale de PAYMENTS_ENCRYPTION_KEY
(o, si no se define, se deriva de SECRET_KEY)."""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet():
    key = getattr(settings, 'PAYMENTS_ENCRYPTION_KEY', '') or settings.SECRET_KEY
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()))


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode() if value else ''


def decrypt(value: str) -> str:
    if not value:
        return ''
    try:
        return _fernet().decrypt(value.encode()).decode()
    except InvalidToken:
        return ''

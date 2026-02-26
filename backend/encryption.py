import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

load_dotenv()

# We need a stable 32-url-safe-base64-encoded key for Fernet.
# We will derive it from the app's SECRET_KEY.
raw_secret = os.getenv("SECRET_KEY", "super_secret_key_fallback")

# Derive a safe 32-byte key for Fernet using a static salt (since this is for at-rest and we need to decrypt consistently)
salt = b"antigravity_static_salt_for_config"
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(raw_secret.encode()))

# Initialize cipher suite
cipher_suite = Fernet(key)

def encrypt_text(plain_text: str) -> str:
    if not plain_text:
        return ""
    return cipher_suite.encrypt(plain_text.encode('utf-8')).decode('utf-8')

def decrypt_text(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    try:
        return cipher_suite.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"Decryption failed: {e}")
        return "[Decryption Error]"

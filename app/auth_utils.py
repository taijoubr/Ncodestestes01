import hashlib
import os
from fastapi import Request
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

SECRET_KEY = "Oloroke_Admin_Secret_Key_2026_Secure!"
signer = TimestampSigner(SECRET_KEY)

def generate_auth_token(user_id: int) -> str:
    """Generates a signed auth token for iframe & multi-tab persistence."""
    return signer.sign(str(user_id)).decode("utf-8")

def verify_auth_token(token: str, max_age: int = 86400) -> int | None:
    """Verifies a signed auth token."""
    if not token:
        return None
    try:
        unsigned = signer.unsign(token, max_age=max_age)
        return int(unsigned.decode("utf-8"))
    except Exception:
        return None

def get_session_user_id(request: Request) -> int | None:
    """
    Retrieves user_id from session cookie or auth_token query parameter / header / cookie.
    Ensures seamless login in both browser top-level tabs and sandboxed iframe previews.
    """
    # 1. Standard session cookie
    user_id = request.session.get("user_id")
    if user_id:
        return user_id

    # 2. Fallback to auth_token query param, header, or custom cookie
    token = (
        request.query_params.get("auth_token") 
        or request.headers.get("X-Auth-Token") 
        or request.cookies.get("oloroke_auth_token")
    )
    if token:
        uid = verify_auth_token(token)
        if uid:
            request.session["user_id"] = uid
            return uid
            
    return None

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2 with SHA-256 and a random salt.
    Format: pbkdf2_sha256$iterations$salt$hash
    """
    salt = os.urandom(16).hex()
    iterations = 100000
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${key}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a pbkdf2_sha256 hashed password.
    """
    try:
        parts = hashed_password.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        iterations = int(parts[1])
        salt = parts[2]
        stored_key = parts[3]
        
        test_key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        ).hex()
        return test_key == stored_key
    except Exception:
        return False


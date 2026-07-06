import hashlib
import os

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

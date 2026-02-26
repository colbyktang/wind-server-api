import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed password."""
    encoded = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(encoded, hashed_password.encode("utf-8"))

def get_password_hash(password: str) -> str:
    """Hashes a plain-text password. Truncates to 72 bytes per bcrypt's limit."""
    encoded = password.encode("utf-8")[:72]
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")
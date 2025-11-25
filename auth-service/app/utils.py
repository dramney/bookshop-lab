from passlib.context import CryptContext
from jose import jwt
import os, time

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret_auth")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(subject: str, role: str, expires=3600):
    payload = {"sub": subject, "role": role, "exp": time.time() + expires}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

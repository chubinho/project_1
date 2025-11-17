from jose import jwt, JWTError
from passlib.hash import bcrypt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


def hash_password(password):
    return bcrypt.hash(password)

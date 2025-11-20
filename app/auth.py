from jose import jwt, JWTError
from passlib.hash import bcrypt
from datetime import datetime, timedelta, timezone
from .config import SECRET_KEY, ALGORITHM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER, APP_URL, EMAIL_FROM
import smtplib
from email.mime.text import MIMEText

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)

def hash_password(password):
    return bcrypt.hash(password)

async def send_verification_email(email: str, token: str):
    link = f"{APP_URL}/verify?token={token}"
    msg = MIMEText(f"Подтвердите email, перейдя по ссылке: {link}")
    msg['Subject'] = "Подтверждение email для FindYourPet"
    msg['From'] = EMAIL_FROM 
    msg['To'] = email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, email, msg.as_string())
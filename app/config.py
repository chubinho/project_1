from os import environ
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = environ.get("SECRET_KEY", "notfound")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 7

if not SECRET_KEY or SECRET_KEY == "notfound":
    raise ValueError("SECRET_KEY не задан в .env")
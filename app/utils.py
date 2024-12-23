from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
import jwt
import datetime
from .extensions import logger
from config import Config

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)

def calculate_commission(user, amount: str) -> Decimal:
    if not user or not user.commission_rate:
        return Decimal("0")
    amt = Decimal(amount)
    rate = Decimal(user.commission_rate)
    return (amt * rate / Decimal("100")).quantize(Decimal("0.01"))

def create_jwt_token(user_id: int, secret_key: str, algorithm: str, expires_minutes: int=60) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + datetime.timedelta(minutes=expires_minutes)
    }
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token

def decode_jwt_token(token: str, secret_key: str, algorithm: str):
    try:
        data = jwt.decode(token, secret_key, algorithms=[algorithm])
        return data
    except jwt.ExpiredSignatureError:
        logger.error("Срок действия токена истёк")
        return None
    except jwt.InvalidTokenError:
        logger.error("Неверный токен")
        return None

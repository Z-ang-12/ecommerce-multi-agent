import os
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token 有效期 60 分钟

def create_access_token(username: str) -> str:
    """为指定用户创建一个 JWT Token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    """验证 Token 是否有效，有效则返回用户名"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise JWTError("无效的用户信息")
        return username
    except JWTError:
        raise JWTError("Token 无效或已过期")
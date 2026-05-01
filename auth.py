from pwdlib import PasswordHash
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from sqlalchemy import select
from fastapi import Depends,HTTPException,status
from .models import User
from .database import get_db
from sqlalchemy.orm import Session

load_dotenv()

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


def create_access_token(payload: dict) -> str:
    if "sub" not in payload:
        raise ValueError("Payload must contain 'sub'")

    to_encode = payload.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, credentials_exception) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        return user_id

    except ExpiredSignatureError:
        raise credentials_exception

    except JWTError:
        raise credentials_exception
    
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")# just used for documentation not in authentication

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception

        user_id: str | None = payload.get("sub")
        if not user_id:
            raise credentials_exception

        try:
            user_id_int = int(user_id)
        except ValueError:
            raise credentials_exception

    except ExpiredSignatureError:
        raise credentials_exception

    except JWTError:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id_int)
    user: User | None = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user    


from fastapi import Depends, HTTPException, status
from typing import List

def require_roles(allowed_roles: List[str]):
    
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: insufficient permissions"
            )
        
        return current_user

    return role_checker
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from .config.settings import pwd_context, oauth2_scheme, SECRET_KEY, ALGORITHM
from .config.database import db

from datetime import datetime, timedelta
from typing import Optional



def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(id: str) -> dict:
    if (user := await db["users"].find_one({"first_name": id})) is not None:
        return user


async def authenticate_user(id: str, password: str) -> dict or bool:
    user = await get_user(id)
    if not user:
        return False
    if not verify_password(password, user["hashed_pass"]):
        return False

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user

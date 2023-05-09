from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Annotated
from sqlalchemy.orm import Session
import crud

SECRET_KEY = "35972854432f36a1bb4d096b2782e69d76aaf48271ae93b84a1d511a20ef6a26"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(client_password: str, hashed_password: str):
    return pwd_context.verify(client_password, hashed_password)


def create_access_token(details: dict, expires: timedelta | None = None):
    to_encode = details

    if expires:
        expires = datetime.utcnow() + expires
    else:
        expires = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expires})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_email(db=db, email=username)

    if user is None:
        return False

    if not verify_password(password, user.password):
        return False
    
    return user


def get_current_user(db: Session, token: Annotated[str, Depends(oath2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = crud.get_user_by_email(db=db, email=username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


def validate_token(db: Session, token: str):
    user = get_current_user(db=db, token=token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # return user
    

def validate_admin_token(db: Session, token: str):
    user = get_current_user(db=db, token=token)
    admin = user.admin_access
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
            headers={"WWW_Authenticate": "Bearer"}
        )

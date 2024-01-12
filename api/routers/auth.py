from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated, List, Optional
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext


router = APIRouter(tags=['Login - Register'], prefix='/users')

db_dependency = Annotated[Session, Depends(get_db)]

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    user = db.query(models.User).filter(models.User.email==username).first()
    if user:
        return user

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False   
    if not verify_password(plain_password=password, hashed_password=user.password):
        return False
    return user

def create_access_token(id: int, username: str, expires_delta: timedelta):
    encode = {'id': id, 'username': username}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("id")
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401)
        return {'id': id, 'username': username}
    except JWTError:
        raise HTTPException(status_code=404)
    

@router.post('/create', status_code=201)
async def register(db: db_dependency, request: schemas.CreateUser):
    new_user = models.User(email=request.email,
                           password=request.password)
    if request.password != request.password2:
        raise HTTPException(status_code=422, detail='Passwords do not match.')
    hashed_password = get_password_hash(request.password)
    new_user.password=hashed_password
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token, status_code=200)
async def login(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(user.id ,user.email, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}
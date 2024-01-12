from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated, List, Optional
from sqlalchemy.orm import Session
from database import get_db
from .auth import get_current_user
import models
import schemas


router = APIRouter(tags=['Users'], prefix='/users')

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Session, Depends(get_current_user)]


@router.get('/', response_model=schemas.User)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=404)
    return db.query(models.User).filter(models.User.id == user.get('id')).first()

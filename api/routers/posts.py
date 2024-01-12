from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated, List, Optional
from sqlalchemy.orm import Session
from database import get_db
from .auth import get_current_user
import models
import schemas


router = APIRouter(tags=['Posts'], prefix='/posts')

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Session, Depends(get_current_user)]

@router.get('/', response_model=List[schemas.GetPost])
async def get_posts(user: user_dependency, db: db_dependency):
    posts = db.query(models.Post).all()
    return posts


@router.get('/{id}', response_model=schemas.GetPost)
async def get_post(db: db_dependency, id: int):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=404)
    return post


@router.post('/', status_code=201)
async def create_post(db: db_dependency, post: schemas.Post):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.put('/{id}')
async def update_post(db: db_dependency, id: int, request: schemas.Post):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=404)
    post.title = request.title
    post.content = request.content
    post.published = request.published
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.delete('/{id}', status_code=204)
async def delete_post(db: db_dependency, id: int):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post is None:
        raise HTTPException(status_code=404)
    post.delete()
    db.commit()

from pydantic import BaseModel
from datetime import datetime

class GetPost(BaseModel):
    id: int
    title: str
    content: str
    created_at : datetime
    
class Post(BaseModel):
    title: str
    content: str
    published: bool = True




class User(BaseModel):
    id: int
    email: str
    created_at: datetime

class CreateUser(BaseModel):
    email: str
    password: str
    password2: str

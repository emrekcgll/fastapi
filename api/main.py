from fastapi import FastAPI
from routers import auth, users, posts
from database import engine
import models

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)

models.Base.metadata.create_all(bind=engine)

@app.get('/')
async def root():
    return {'god': 'Hell World'}

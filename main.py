# HELP!
from fastapi import FastAPI, Depends
from controllers.teas import router as TeasRouter
from controllers.comments import router as CommentsRouter
from controllers.users import router as UsersRouter
from typing import Optional

app = FastAPI()
# app.include_router(TeasRouter, prefix='/api')
# app.include_router(CommentsRouter, prefix='/api')
app.include_router(UsersRouter, prefix="/api") 

@app.get('/')
def home():
    return {'msg': 'HELP!'}


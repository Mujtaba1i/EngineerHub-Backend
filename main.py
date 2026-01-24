# HELP!
from fastapi import FastAPI, Depends
from controllers.auth import router as AuthRouter
from controllers.classes import router as ClassesRouter
from controllers.role import router as RoleRouter
from controllers.students_classes import router as Students_ClassesRouter
from controllers.users import router as UsersRouter
from typing import Optional

app = FastAPI()
app.include_router(ClassesRouter, prefix='/api')
app.include_router(RoleRouter, prefix='/api')
app.include_router(AuthRouter, prefix='/api')
app.include_router(Students_ClassesRouter, prefix='/api')
app.include_router(UsersRouter, prefix="/api") 

@app.get('/')
def home():
    return {'msg': 'HELP!'}


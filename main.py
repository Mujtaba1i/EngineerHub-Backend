# HELP!
from fastapi import FastAPI, Depends
from controllers.auth import router as AuthRouter
from controllers.classes import router as ClassesRouter
from controllers.students_classes import router as Students_ClassesRouter
from controllers.users import router as UsersRouter
from controllers.announcements import router as AnnouncementsRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # Which sites can call this API
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],       # Allow all headers (e.g., Content-Type, Authorization)
    # NOTE: We are NOT using credentials in this simple lesson,
    # so we are not setting allow_credentials.
)

app.include_router(ClassesRouter, prefix='/api')
app.include_router(AuthRouter, prefix='/api')
app.include_router(Students_ClassesRouter, prefix='/api')
app.include_router(UsersRouter, prefix="/api") 
app.include_router(AnnouncementsRouter, prefix="/api")

@app.get('/')
def home():
    return {'msg': 'HELP!'}
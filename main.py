# HELP!
from fastapi import FastAPI, Depends
from controllers.auth import router as AuthRouter
from controllers.classes import router as ClassesRouter
from controllers.students_classes import router as Students_ClassesRouter
from controllers.users import router as UsersRouter
from controllers.graduates_projects import router as Graduate_ProjectRouter
from controllers.announcements import router as AnnouncementsRouter
from controllers.notes import router as NotesRouter
from controllers.posts import router as PostsRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(AuthRouter, prefix='/api')
app.include_router(ClassesRouter, prefix='/api')
app.include_router(Students_ClassesRouter, prefix='/api')
app.include_router(UsersRouter, prefix="/api") 
app.include_router(Graduate_ProjectRouter, prefix="/api") 
app.include_router(AnnouncementsRouter, prefix="/api")
app.include_router(NotesRouter, prefix="/api")
app.include_router(PostsRouter, prefix="/api")

@app.get('/')
def home():
    return {'msg': 'HELP!'}
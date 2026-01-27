from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.graduate_project import GraduateProjectModel
from serializers.graduate_project import ( GraduateProjectCreateSchema, GraduateProjectSchema, GraduateProjectUpdateSchema)
from dependencies.get_current_user import get_current_user

router = APIRouter()

# GET ALL ================================================================================================
@router.get("/projects", response_model=list[GraduateProjectSchema])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(GraduateProjectModel).all()
    return projects


# GET ONE ================================================================================================
@router.get("/projects/{project_id}", response_model=GraduateProjectSchema)
def get_single_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(GraduateProjectModel)\
        .filter(GraduateProjectModel.id == project_id)\
        .first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# CREATE ================================================================================================
@router.post("/projects", response_model=GraduateProjectSchema)
def create_project(
    data: GraduateProjectCreateSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    project = GraduateProjectModel(**data.dict(), user_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# UPDATE ===============================================================================================
@router.put("/projects/{project_id}", response_model=GraduateProjectSchema)
def update_project( project_id: int, data: GraduateProjectUpdateSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = db.query(GraduateProjectModel)\
        .filter(GraduateProjectModel.id == project_id)\
        .first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


# DELETE =======================================================================================================
@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = db.query(GraduateProjectModel)\
        .filter(GraduateProjectModel.id == project_id)\
        .first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

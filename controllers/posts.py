from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import  UserModel
from models.post import PostModel
from serializers.post import PostCreateSchema, PostUpdateSchema, PostSchema
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()


# GET ALL ============================================================================
@router.get("/posts", response_model=list[PostSchema])
def get_my_posts(current_institute: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = db.query(PostModel).filter(PostModel.institute_id == current_institute.id).all()
    return posts

# GET ONE ===========================================================================
@router.get("/posts/{post_id}", response_model=PostSchema)
def get_single_post(post_id: int, current_institute: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id, PostModel.institute_id == current_institute.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# CREATE =============================================================================
@router.post("/posts", response_model=PostSchema)
def create_post(post: PostCreateSchema, current_institute: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_institute.role != "institution":
        raise HTTPException(status_code=403, detail="Only institutions can create posts")
    new_post = PostModel(**post.dict(), institute_id=current_institute.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# UPDATE =============================================================================
@router.put("/posts/{post_id}", response_model=PostSchema)
def update_post(post_id: int, post_update: PostUpdateSchema, current_institute: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id, PostModel.institute_id == current_institute.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post_update.dict(exclude_unset=True).items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post

# DELETE ===============================================================================
@router.delete("/posts/{post_id}")
def delete_post(post_id: int, current_institute: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id, PostModel.institute_id == current_institute.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"detail": "Post deleted successfully"}

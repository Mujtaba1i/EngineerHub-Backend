from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.tea_db import TeaModel
from models.comment import CommentModel
from models.user import UserModel
from serializers.tea import *
from serializers.comment import *
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()

@router.get('/teas/{tea_id}/comments', response_model=list[CommentSchema])
def get_tea_comments(tea_id: int, db: Session = Depends(get_db)):
    one_tea = db.query(TeaModel).filter(TeaModel.id == tea_id).first()
    if not one_tea:
        raise HTTPException(status_code=404, detail="Tea not found")
    return one_tea.comments

@router.get('/comments/{comment_id}', response_model=CommentSchema)
def get_one_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.post('/teas/{tea_id}/comments', response_model=CommentSchema)
def create_comment(tea_id: int, comment: CreateCommentSchema,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    tea = db.query(TeaModel).filter(TeaModel.id == tea_id).first()
    new_comment = CommentModel(**comment.dict())
    new_comment.tea = tea
    new_comment.user_id = current_user.id
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.put('/comments/{comment_id}', response_model=CommentSchema)
def update_comment(comment_id:int, comment: UpdateCommentSchema, db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    db_comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Operation forbidden")
    
    comment_data = comment.dict(exclude_unset=True)

    for key, value in comment_data.items():
        setattr(db_comment, key, value)
    
    db.commit()
    db.refresh(db_comment)

    return db_comment

@router.delete('/comments/{comment_id}')
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Operation forbidden")
    db.delete(comment)
    db.commit()
    return {"message": f"Comment with ID {comment_id} has been deleted"}



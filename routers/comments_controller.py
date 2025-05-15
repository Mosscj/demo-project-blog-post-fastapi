from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database, auth

router = APIRouter(prefix="/comments", tags=["Comments"])

def build_comment_tree(comments):
    comment_map = {c.id: c for c in comments}
    root_comments = []

    for c in comments:
        c.replies = []

    for comment in comments:
        if comment.parent_id:
            parent = comment_map.get(comment.parent_id)
            if parent:
                parent.replies.append(comment)
        else:
            root_comments.append(comment)

    return root_comments

@router.post("/posts/{post_id}", response_model=schemas.CommentOut)
def create_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.get_current_user)):
    if comment.parent_id:
        parent = db.query(models.Comment).filter(models.Comment.id == comment.parent_id).first()
        if not parent or parent.post_id != post_id:
            raise HTTPException(status_code=400, detail="Invalid parent comment")

    db_comment = models.Comment(
        content=comment.content,
        owner_id=current_user.id,
        post_id=post_id,
        parent_id=comment.parent_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/posts/{post_id}", response_model=List[schemas.CommentOut])
def get_comments(post_id: int, db: Session = Depends(database.SessionLocal)):
    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(models.Comment.timestamp.asc()).all()
    return build_comment_tree(comments)

@router.put("/{comment_id}", response_model=schemas.CommentOut)
def update_comment(comment_id: int, updated: schemas.CommentCreate, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    comment.content = updated.content
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

from .. import models, schemas, utils
from fastapi import FastAPI, Response, status,HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. database import  get_db
from .. import oauth2, schemas, models
from typing import List, Optional
from sqlalchemy import func

router = APIRouter(
    prefix = "/posts" ,
     tags = ['Posts']
)

@router.get("/" ,response_model = List[schemas.PostOut])
# @router.get("/")
def get_posts(db:Session = Depends(get_db),current_user : int = 
                 Depends(oauth2.get_current_user), limit:int = 10, skip:int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    # print(posts)

    # results = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    results = db.query( models.Post,  # type: ignore
                        func.count(models.Vote.post_id).label("votes")
                    ).join(
                        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
                    ).group_by(
                        models.Post.id
                    ).filter(
                        models.Post.title.contains(search)
                    ).limit(limit).offset(skip).all()
    print("checking results")
    return results
    # return [{**r[0].model_dump(), "votes": r[1]} for r in results]
    # return [{"post": r[0], "votes": r[1]} for r in results]

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= schemas.Post)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db), current_user : int = 
                 Depends(oauth2.get_current_user)):
 
    
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, # to prevent sql injection
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit() # to save the changes in the database
    
    # print(**post.model_dump())
    new_posts = models.Post(owner_id = current_user.id, **post.model_dump()) # type: ignore
    db.add(new_posts)
    db.commit()
    db.refresh(new_posts)

    return new_posts
# title str, content str 
@router.get("/{id}", response_model= schemas.PostOut)
# @router.get("/{id}")
def get_post(id:int, db : Session = Depends(get_db), current_user : int = 
                 Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    # print(post)
    
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query( models.Post,
                        func.count(models.Vote.post_id).label("votes")
                    ).join(
                        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
                    ).group_by( # type: ignore
                        models.Post.id
                    ).filter(
                        models.Post.id == id
                    ).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                             detail = f"post with id: {id} was not found")
     
    return post

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db:Session = Depends(get_db), current_user : int = 
                 Depends(oauth2.get_current_user)):


    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id) # type: ignore
    post = post_query.first()
    if post== None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                             detail = f"post with id: {id} was not found")
    if post.owner_id != current_user.id: # type: ignore
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                             detail = f"Not authorized to perform requested action")
    post_query.delete(synchronize_session = False)
    db.commit()

    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model = schemas.Post)
def update_post(id:int, updated_post:schemas.PostCreate, db:Session = Depends(get_db), current_user : int = 
                 Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s Where id = %s RETURNING *""",
    #                 (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id) # type: ignore
    post = post_query.first()


    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                             detail = f"post with id: {id} was not found")
    
    if post.owner_id != current_user.id: # type: ignore
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                             detail = f"Not authorized to perform requested action")

    post_query.update(updated_post.model_dump(), synchronize_session = False)
    db.commit()
    return  post_query.first()


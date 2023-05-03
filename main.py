from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
    

@app.post('/users/', response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered!")
    return crud.create_user(db=db, user=user)

@app.get('/users/', response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db=db)
    return users

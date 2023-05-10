from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import timedelta
from database import SessionLocal, engine
from utils import query_filter
import models, schemas, crud, security

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

## Start of Dependencies
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_token_header(token: Annotated[str, Header()]):
    return token
## end of Dependencies
    

# login
@app.post('/token', response_model=schemas.Token)
def generate_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = security.authenticate_user(db=db, username=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_exp = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = security.create_access_token(
        details={"sub": user.email},
        expires=access_token_exp
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post('/api/users/', response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered!")
    return crud.create_user(db=db, user=user)

@app.get('/api/users/', response_model=list[schemas.User])
def read_users(token: Annotated[str, Depends(get_token_header)], db: Session = Depends(get_db)):
    security.validate_admin_token(db=db, token=token)
    
    users = crud.get_users(db=db)
    return users


@app.post('/api/hotel/rooms/', response_model=schemas.Room)
def add_room(token: Annotated[str, Depends(security.oath2_scheme)], room: schemas.RoomBase, db: Session = Depends(get_db)):
    security.validate_admin_token(db=db, token=token)
    
    db_room = crud.get_room_by_room_number(db=db, room_number=room.room_number)
    if db_room:
        raise HTTPException(status_code=400, detail=f"Room {room.room_number} already added!")
    return crud.add_room(db=db, room=room)

@app.get('/api/hotel/rooms/', response_model=list[schemas.Room])
def get_rooms(
    token: Annotated[str, Depends(security.oath2_scheme)],
    db: Session = Depends(get_db), 
    room_number: str | None = None, 
    floor: int | None = None, 
    number_of_bedrooms: int | None = None, 
    occupancy_limit: int | None = None, 
    status: schemas.Status | None = None
):
    security.validate_token(db=db, token=token)
    
    query = {
        "room_number": room_number,
        "floor": floor,
        "number_of_bedrooms": number_of_bedrooms, 
        "occupancy_limit": occupancy_limit,
        "status": status.lower() if status is not None else status
    }

    filter = query_filter(query)

    rooms = crud.get_rooms_by_filter(db=db, filter=filter)
    return rooms

@app.put('/api/hotel/rooms/{room_number}', response_model=schemas.Room)
def update_room_price(room_number: str, price: str, token: Annotated[str, Depends(security.oath2_scheme)], db: Session = Depends(get_db)):
    security.validate_admin_token(db=db, token=token)
    
    room = crud.get_room_by_room_number(db=db, room_number=room_number)
    return crud.update_room_info(db=db, room_id=room.id, value_to_update={"price": price})

@app.put('/api/hotel/rooms/check-out/{reference}', response_model=schemas.Room)
def update_room(token: Annotated[str, Depends(security.oath2_scheme)], reference: str, db:Session = Depends(get_db)):
    security.validate_token(db=db, token=token)
    
    booking = crud.get_booking(db=db, reference=reference)
    return crud.update_room_info(db=db, room_id=booking.room_id, value_to_update={"status": "available"})



@app.post('/api/hotel/bookings/', response_model=schemas.Booking)
def create_booking(token: Annotated[str, Depends(security.oath2_scheme)], booking: schemas.BookingBase, db: Session = Depends(get_db)):
    security.validate_token(db=db, token=token)
        
    return crud.create_booking(db, booking=booking)
    

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from utils import query_filter
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
    

@app.post('/api/users/', response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered!")
    return crud.create_user(db=db, user=user)

@app.get('api/users/', response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db=db)
    return users


@app.post('/api/hotel/rooms/', response_model=schemas.Room)
def add_room(room: schemas.RoomBase, db: Session = Depends(get_db)):
    db_room = crud.get_room_by_room_number(db=db, room_number=room.room_number)
    if db_room:
        raise HTTPException(status_code=400, detail=f"Room {room.room_number} already added!")
    return crud.add_room(db=db, room=room)

@app.get('/api/hotel/rooms/', response_model=list[schemas.Room])
def get_rooms(db: Session = Depends(get_db), room_number: str | None = None, floor: int | None = None, number_of_bedrooms: int | None = None, occupancy_limit: int | None = None, status: models.Status | None = None):
    query = {
        "room_number": room_number,
        "floor": floor,
        "number_of_bedrooms": number_of_bedrooms, 
        "occupancy_limit": occupancy_limit,
        "status": status.lower()
    }

    filter = query_filter(query)

    rooms = crud.get_rooms_by_filter(db=db, filter=filter)
    return rooms

@app.put('/api/hotel/rooms/{room_number}', response_model=schemas.Room)
def update_room_price(room_number: str, price: str, db: Session = Depends(get_db)):
    room = crud.get_room_by_room_number(db=db, room_number=room_number)
    return crud.update_room_info(db=db, room_id=room.id, value_to_update={"price": price})

@app.put('/api.hotel/rooms/check-out/{reference}', response_model=schemas.Room)
def update_room(reference: str, db:Session = Depends(get_db)):
    booking = crud.get_booking(db=db, reference=reference)
    return crud.update_room_info(db=db, room_id=booking.room_id, value_to_update={"status": "available"})



@app.post('/api/hotel/bookings/', response_model=schemas.Booking)
def create_booking(booking: schemas.BookingBase, db: Session = Depends(get_db)):
    return crud.create_booking(db, booking=booking)




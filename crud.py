from sqlalchemy.orm import Session
from datetime import datetime
from utils import createReferenceNumber
import models, schemas, security


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# ///////////////////////////////////////////////
def get_users(db: Session):
    return db.query(models.User).all()
# ///////////////////////////////////////////////


def create_user(db: Session, user: schemas.UserBase):
    hashed_password = security.get_password_hash(password=user.password)
    db_user = models.User(firstname=user.firstname, lastname=user.lastname, email=user.email, phone_number=user.phone_number, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def add_room(db: Session, room: schemas.RoomBase):
    db_room = models.Room(room_number=room.room_number, floor=room.floor, number_of_bedrooms=room.number_of_bedrooms, bed_type=room.bed_type, occupancy_limit=room.occupancy_limit, ammenities=room.ammenities, status=room.status, price=room.price)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_rooms(db: Session):
    return db.query(models.Room).all()

def get_room_by_room_number(db: Session, room_number: str):
    return db.query(models.Room).filter(models.Room.room_number == room_number).first()

def get_rooms_by_floor(db: Session, floor_number: int):
    return db.query(models.Room).filter(models.Room.floor == floor_number).all()

def get_rooms_by_number_of_bedrooms(db: Session, number_of_bedrooms: int):
    return db.query(models.Room).filter(models.Room.number_of_bedrooms == number_of_bedrooms).all()

def get_rooms_by_occupancy_limit(db: Session, occupancy_limit: int):
    return db.query(models.Room).filter(models.Room.occupancy_limit == occupancy_limit).all()

def get_rooms_by_status(db: Session, status: str):
    return db.query(models.Room).filter(models.Room.status == status).all()

def get_rooms_by_filter(db: Session, filter: dict):
    if filter:
        keys = list(filter.keys())

        if len(keys) == 1:
            return db.query(models.Room).filter(
                models.Room.__dict__[keys[0]] == filter[keys[0]]
            ).all()
        elif len(keys) == 2:
            return db.query(models.Room).filter(
                models.Room.__dict__[keys[0]] == filter[keys[0]], 
                models.Room.__dict__[keys[1]] == filter[keys[1]]
            ).all()
        elif len(keys) == 3:
            return db.query(models.Room).filter(
                models.Room.__dict__[keys[0]] == filter[keys[0]], 
                models.Room.__dict__[keys[1]] == filter[keys[1]], 
                models.Room.__dict__[keys[2]] == filter[keys[2]]
            ).all()
        elif len(keys) == 4:
            return db.query(models.Room).filter(
                models.Room.__dict__[keys[0]] == filter[keys[0]], 
                models.Room.__dict__[keys[1]] == filter[keys[1]], 
                models.Room.__dict__[keys[2]] == filter[keys[2]], 
                models.Room.__dict__[keys[3]] == filter[keys[3]]
            ).all()
        
        return db.query(models.Room).filter(
            models.Room.__dict__[keys[0]] == filter[keys[0]], 
            models.Room.__dict__[keys[1]] == filter[keys[1]], 
            models.Room.__dict__[keys[2]] == filter[keys[2]], 
            models.Room.__dict__[keys[3]] == filter[keys[3]], 
            models.Room.__dict__[keys[4]] == filter[keys[4]]
        ).all()

    return db.query(models.Room).all()

def update_room_info(db: Session, room_id: int, value_to_update: dict):
    key = list(value_to_update.keys())[0]
    value = value_to_update[key]

    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return db_room

# price


def get_booking(db: Session, reference: str):
    return db.query(models.Booking).filter(models.Booking.reference == reference).first()

def create_booking(db: Session, booking: schemas.BookingBase):
    room = db.query(models.Room).filter(models.Room.id == booking.room_id).first()
    if room.status == 'available':
        reference = createReferenceNumber(room_number=room.room_number)
        db_booking = models.Booking(
            reference=reference, 
            booking_date=datetime.now(), 
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            price=booking.price, 
            customer_id=booking.customer_id, 
            room_id=booking.room_id
        )
        room.status = 'booked'
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
    return db_booking
    
def get_booking_info(db: Session, reference: str):
    return db.query(models.Booking).filter(models.Booking.reference == reference).first()

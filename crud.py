from sqlalchemy.orm import Session
import models, schemas


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# ///////////////////////////////////////////////
def get_users(db: Session):
    return db.query(models.User).all()
# ///////////////////////////////////////////////


def create_user(db: Session, user: schemas.UserBase):
    db_user = models.User(firstname=user.firstname, lastname=user.lastname, email=user.email, phone_number=user.phone_number, password=user.password)
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
    return db.query(models.Room).filter(room_number=room_number).first()

def get_rooms_by_floor(db: Session, floor_number: int):
    return db.query(models.Room).filter(floor_number=floor_number).all()

def get_rooms_by_number_of_bedrooms(db: Session, number_of_bedrooms: int):
    return db.query(models.Room).filter(number_of_bedrooms=number_of_bedrooms).all()

def get_rooms_by_occupancy_limit(db: Session, occupancy_limit: int):
    return db.query(models.Room).filter(occupancy_limit=occupancy_limit).all()

def get_rooms_by_status(db: Session, status: str):
    return db.query(models.Room).filter(status=status).all()

# price
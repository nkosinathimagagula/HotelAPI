from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    phone_number = Column(String)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True)
    floor = Column(Integer)
    number_of_bedrooms = Column(Integer)
    bed_type = Column(String)
    occupancy_limit = Column(Integer)
    ammenities = Column(String)
    status = Column(String)
    price = Column(Float)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True)
    booking_date = Column(Date)
    check_in_date = Column(Date)
    check_out_date = Column(Date)
    price = Column(Float)

    customer_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))


# reviews 


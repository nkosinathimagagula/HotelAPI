from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: str
    phone_number: str
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class RoomBase(BaseModel):
    room_number: str
    floor: int
    number_of_bedrooms: int
    bed_type: str
    occupancy_limit: int
    ammenities: str
    status: str
    price: float


class Room(RoomBase):
    id: int

    class Config:
        orm_mode = True



class BookingBase(BaseModel):
    check_in_date: date
    check_out_date: date
    price: float

    customer_id: int = Field(gt=0, description="The customer id must be greater than 0")
    room_id: int = Field(gt=0, description="The room id must be greater tha 0")


class Booking(BookingBase):
    id: int
    reference: str
    booking_date: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class Status(str, Enum):
    available = "Available"
    Booked = "Booked"

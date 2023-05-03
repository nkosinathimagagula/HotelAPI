from pydantic import BaseModel
from datetime import datetime


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
    reference: str
    booking_date: datetime
    booking_date: datetime
    check_in_date: datetime
    check_out_date: datetime
    price: float

    customer_id: int
    room_id: int


class Booking(BookingBase):
    id: int

    class Config:
        orm_mode = True

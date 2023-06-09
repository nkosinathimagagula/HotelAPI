from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db
import models, security


SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Users\\nkosinathi\\Documents\\vscode\\APIs\\HotelApi\\sqlalchemy_database\\test_database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def overide_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

    
app.dependency_overrides[get_db] = overide_get_db

client = TestClient(app)


def test_generate_access_token_for_user():
    response = client.post(
        '/token', 
        data={"username": "test@user.com", "password": "testuserpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert type(data["access_token"]) == str
    assert data["token_type"] == "bearer"


def test_generate_access_token_for_admin():
    response = client.post(
        '/token',
        data={"username": "test@admin.com", "password": "testadminpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert type(data["access_token"]) == str
    assert data["token_type"] == "bearer"


def test_generate_access_token_for_non_user():
    response = client.post(
        '/token', 
        data={"username": "notAuser", "password": "dummypassword", "grant_type": "password"}, 
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"] == "Incorrect username or password"
    
    
def test_create_user():
    response = client.post(
        '/api/users', 
        json={
            "firstname": "unit",
            "lastname": "testing",
            "email": "unit@testing.com",
            "phone_number": "0000000000",
            "password": "unittesting"
        }
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert data["firstname"] == "unit"
    assert data["lastname"] == "testing"
    assert data["email"] == "unit@testing.com"
    assert data["phone_number"] == "0000000000"
    assert security.verify_password("unittesting", data["password"])
    assert data["admin_access"] == False
    
    # DELETE THE USER CREATED IN THE DATABASE
    db = TestingSessionLocal()
    created_user = db.query(models.User).filter(models.User.email == 'unit@testing.com').first()
    db.delete(created_user)
    db.commit()
    db.close()
    
    
def test_create_user_for_email_already_registered():
    response = client.post(
        '/api/users/',
        json={
            "firstname": "test",
            "lastname": "user",
            "email": "test@user.com",
            "phone_number": "0000000000",
            "password": "testuserpassword"
        }
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Email already registered!"
    

def test_get_users_for_admin():
    admin_token = client.post(
        '/token',
        data={"username": "test@admin.com", "password": "testadminpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.get(
        '/api/users',
        headers={"Authorization": f"bearer {admin_token}"}
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert type(data) == list
    assert list(data[0].keys()) == ["firstname", "lastname", "email", "phone_number", "password", "admin_access", "id"]


def test_get_users_for_user():
    user_token = client.post(
        '/token',
        data={"username": "test@user.com", "password": "testuserpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.get(
        '/api/users',
        headers={"Authorization": f"bearer {user_token}"}
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"] == "Invalid admin token"


def test_add_room_for_admin():
    admin_token = client.post(
        '/token',
        data={"username": "test@admin.com", "password": "testadminpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.post(
        '/api/hotel/rooms/',
        headers={"Authorization": f"bearer {admin_token}"},
        json={
            "room_number": "AP0001",
            "floor": 0,
            "number_of_bedrooms": 3,
            "bed_type": "single, single, double",
            "occupancy_limit": 4,
            "ammenities": "amenity1, amenity2, amenity3",
            "status": 'available',
            "price": 600.00,
        }
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert data['room_number'] == "AP0001"
    assert data['floor'] == 0
    assert data['number_of_bedrooms'] == 3
    assert data['bed_type'] == "single, single, double"
    assert data['occupancy_limit'] == 4
    assert data['ammenities'] == 'amenity1, amenity2, amenity3'
    assert data['status'] == "available"
    assert data['price'] == 600.00
    

def test_add_room_for_admin_when_adding_existing_room():
    admin_token = client.post(
        '/token',
        data={"username": "test@admin.com", "password": "testadminpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.post(
        '/api/hotel/rooms/',
        headers={"Authorization": f"bearer {admin_token}"},
        json={
            "room_number": "AP0001",
            "floor": 0,
            "number_of_bedrooms": 3,
            "bed_type": "single, single, double",
            "occupancy_limit": 4,
            "ammenities": "amenity1, amenity2, amenity3",
            "status": 'available',
            "price": 600.00,
        }
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data['detail'] == "Room AP0001 already added!"
    
    
    
    # DELETE THE ROOM CREATED IN THE DATABASE (might need it later...)
    db = TestingSessionLocal()
    added_room = db.query(models.Room).filter(models.Room.room_number == 'AP0001').first()
    db.delete(added_room)
    db.commit()
    db.close()


def test_add_room_for_user():
    user_token = client.post(
        '/token',
        data={"username": "test@user.com", "password": "testuserpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.post(
        '/api/hotel/rooms/',
        headers={"Authorization": f"bearer {user_token}"},
        json={
            "room_number": "AP0001",
            "floor": 0,
            "number_of_bedrooms": 3,
            "bed_type": "single, single, double",
            "occupancy_limit": 4,
            "ammenities": "amenity1, amenity2, amenity3",
            "status": 'available',
            "price": 600.00,
        }
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data['detail'] == "Invalid admin token"



def test_get_rooms():
    user_token = client.post(
        '/token',
        data={"username": "test@user.com", "password": "testuserpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.get(
        '/api/hotel/rooms/',
        headers={"Authorization": f"bearer {user_token}"}
    )
    
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert type(data) == list
    

def test_get_rooms_with_query_filters():
    user_token = client.post(
        '/token',
        data={"username": "test@user.com", "password": "testuserpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.get(
        '/api/hotel/rooms/?status=Available&floor=1',
        headers={"Authorization": f"bearer {user_token}"}
    )
    
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert type(data) == list
    

def test_get_rooms_with_all_query_filters():
    user_token = client.post(
        '/token',
        data={"username": "test@user.com", "password": "testuserpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.get(
        '/api/hotel/rooms/?room_number=AP1102&floor=1&number_of_bedrooms=2&occupancy_limit=4&status=Available',
        headers={"Authorization": f"bearer {user_token}"}
    )
    
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert type(data) == list
    
    
def test_update_room_price():
    admin_token = client.post(
        '/token',
        data={"username": "test@admin.com", "password": "testadminpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.put(
        '/api/hotel/rooms/AP1101',
        headers={"Authorization": f"bearer {admin_token}"},
        json={"price": 20.00}
    )    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert data['room_number'] == "AP1101"
    assert data['floor'] == 1
    assert data['price'] == 20.00
    

def test_create_booking():
    user_token = client.post(
        '/token',
        data={"username": "test@user.com", "password": "testuserpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.post(
        '/api/hotel/bookings/',
        headers={"Authorization": f"bearer {user_token}"},
        json={
            "check_in_date": "2023-08-10",
            "check_out_date": "2023-08-15",
            "price": 900,
            "customer_id": 2,
            "room_id": 7
        }
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert type(data['reference']) == str
    
    
    # DELETE THE BOOKING CREATED IN THE DATABASE AND CHANGE THE ROOM STATUS
    db = TestingSessionLocal()
    
    created_booking = db.query(models.Booking).filter(models.Booking.reference == data['reference']).first()
    room = db.query(models.Room).filter(models.Room.id == 7).first()
    
    room.status = "available"
    
    db.delete(created_booking)
    
    db.commit()
    db.close()
    
    

def test_update_room():
    admin_token = client.post(
        '/token',
        data={"username": "test@admin.com", "password": "testadminpassword", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    ).json()['access_token']
    
    response = client.put(
        f"/api/hotel/rooms/check-out/dummyreference",
        headers={"Authorization": f"bearer {admin_token}"}
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert data['status'] == "available"
    
    
    

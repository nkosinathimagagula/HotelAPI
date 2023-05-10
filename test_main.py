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

current_test_token_for_user = {"token": ''}
current_test_token_for_admin = {"token": ''}

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
    
    current_test_token_for_user["token"] = data["access_token"]


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
    
    current_test_token_for_admin["token"] = data["access_token"]


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
    response = client.get(
        '/api/users',
        headers={"Authorization": f"bearer {current_test_token_for_admin['token']}"}
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_200_OK
    assert type(data) == list
    assert list(data[0].keys()) == ["firstname", "lastname", "email", "phone_number", "password", "admin_access", "id"]


def test_get_users_for_user():
    response = client.get(
        '/api/users',
        headers={"Authorization": f"bearer {current_test_token_for_user['token']}"}
    )
    
    data = response.json()
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data["detail"] == "Invalid admin token"
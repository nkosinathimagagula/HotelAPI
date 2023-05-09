from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Users\\nkosinathi\\Documents\\vscode\\APIs\\HotelApi\\sqlalchemy_database\\test.db"

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


def test_generate_access_token():
    response = client.post(
        '/token', 
        data={"username": "test@user.com", "password": "testuserpassword", "grant_type": "password"}, 
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
    
    
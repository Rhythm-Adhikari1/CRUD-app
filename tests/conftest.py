from fastapi.testclient import TestClient
from app.main import app
from app import schemas
from app.database import engine, get_db
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db
from app import models
import pytest # type: ignore
from alembic import command # type: ignore
from app.oauth2 import create_access_token

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:password123@localhost:5432/fastapi_test'
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@\
{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
 
engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit= False, autoflush = False,
                             bind = engine)

@pytest.fixture(scope = 'function')
def session():
    models.Base.metadata.drop_all(bind=engine) # type: ignore
    models.Base.metadata.create_all(bind=engine) # type: ignore
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope = 'function')
def client(session):

    def override_get_db():
        try:
            yield session
        finally:
            session.close()
  
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    
    
@pytest.fixture
def test_user(client):
    user_data = {"email": "test@example.com", 
                 "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    res.json()
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def test_user2(client):
    user_data = {"email": "test2@example.com", 
                 "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    res.json()
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client

@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {"title": "first title", "content": "first content", "owner_id": test_user['id']},
        {"title": "second title", "content": "second content", "owner_id": test_user['id']},
        {"title": "third title", "content": "third content", "owner_id": test_user['id']},
        {"title": "fourth title", "content": "fourth content", "owner_id": test_user2['id']},
    ]

    session.add_all([models.Post(**post) for post in posts_data])
    session.commit()
    posts = session.query(models.Post).all()
    return posts
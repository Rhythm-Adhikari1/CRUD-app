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

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:password123@localhost:5432/fastapi_test'
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@\
{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

print(SQLALCHEMY_DATABASE_URL)
 
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
    
    
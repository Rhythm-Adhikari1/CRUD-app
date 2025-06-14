import pytest # type: ignore
from app import schemas
from .database import client, session
from jose import jwt # type: ignore
from app.config import settings


# def test_root(client):
#     res = client.get("/")
#     print(res.json().get('message'))
#     assert res.json().get('message') == "welcome to my api!"
#     assert res.status_code == 200



def test_create_user(client):
    res = client.post("/users/", json={"email": "test@example.com", "password": "password123"})
    new_user = schemas.UserOut(**res.json())
    assert res.status_code == 201
    assert new_user.email == "test@example.com"


def test_login_user(test_user, client):
    res = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload.get("user_id") # type: ignore
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200
    assert "access_token" in res.json()

@pytest.mark.parametrize("email, password,status_code", [
    ("invalidemail.com", "password123", 403),
    ("asdf", "password123", 403),
    (None, "password123", 422),
    ("ridam@gmail.com", None, 422),
])
def test_incorrect_login(test_user,client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code
    if status_code == 403:
        assert res.json().get("detail") == "Invalid Credentials"
    elif status_code == 422:
        assert res.json().get("detail") == "Validation Error"

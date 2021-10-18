from utils import get_db
from fastapi.testclient import TestClient
from main import myapp
from dotenv import load_dotenv
from os import getenv
from secrets import token_urlsafe

load_dotenv()

admin_token = getenv("ADMIN_TOKEN")

client = TestClient(myapp)


# global variables
user_token = ""
random_user = f"{token_urlsafe(8)}@we45.com"
random_group = f"{token_urlsafe(8)}-group"


def test_get_db():
    db = get_db()
    assert db is not None


def test_create_user():
    response = client.put(
        "/user/create", json={"email": random_user, "password": "hungry123"}
    )
    assert response.status_code == 200
    assert response.json().get("success")


def test_user_login():
    response = client.post(
        "/user/login", json={"email": random_user, "password": "hungry123"}
    )

    assert response.status_code == 200
    assert response.json().get("success")
    global user_token
    user_token = response.json().get("data").get("token")


def test_create_group():
    response = client.post(
        "/group/create",
        json={"name": random_group, "description": "this is a test user group"},
        headers={"Authorization": admin_token},
    )
    assert response.status_code == 200
    assert response.json().get("success")


def test_assign_user_to_group():
    response = client.post(
        "/group/assign",
        json={"email": random_user, "group_name": random_group},
        headers={"Authorization": admin_token},
    )
    assert response.status_code == 200
    assert response.json().get("success")


def test_create_namespace():
    response = client.put(
        "/namespace/create",
        headers={"Authorization": admin_token},
        json={"name": "test-namespace", "description": "this is the test namespace"},
    )
    assert response.status_code == 200
    assert response.json().get("success")


def test_list_namespaces():
    response = client.get("/namespace/list", headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert response.json().get("success")


def test_get_namespaces():
    response = client.post(
        "/namespace/get",
        headers={"Authorization": admin_token},
        json={"name": "test-namespace"},
    )
    assert response.status_code == 200
    assert response.json().get("success")

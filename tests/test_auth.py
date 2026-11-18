from app.extensions import db
from app.models import User

from .conftest import login


def test_password_is_hashed(make_user):
    user = make_user()
    assert user.password_hash != "secret123"
    assert user.check_password("secret123")
    assert not user.check_password("wrong")


def test_register_creates_user(client, app):
    res = client.post("/auth/register", data={
        "username": "bob", "email": "Bob@Example.com",
        "password": "password123", "confirm": "password123",
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Account created" in res.data
    assert db.session.query(User).filter_by(email="bob@example.com").first() is not None


def test_register_rejects_duplicate_and_mismatch(client, make_user):
    make_user()
    res = client.post("/auth/register", data={
        "username": "alice", "email": "alice@example.com",
        "password": "password123", "confirm": "different",
    })
    assert b"already taken" in res.data
    assert b"already registered" in res.data
    assert b"Passwords must match" in res.data


def test_login_logout_flow(client, make_user):
    make_user()
    res = login(client)
    assert b"Welcome back, alice" in res.data
    res = client.post("/auth/logout", follow_redirects=True)
    assert b"logged out" in res.data


def test_login_wrong_password(client, make_user):
    make_user()
    res = login(client, password="nope")
    assert res.status_code == 401
    assert b"Invalid email or password" in res.data


def test_protected_route_redirects_to_login(client):
    res = client.get("/posts/new")
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]


def test_open_redirect_is_blocked(client, make_user):
    make_user()
    res = client.post("/auth/login?next=https://evil.example.com",
                      data={"email": "alice@example.com", "password": "secret123"})
    assert res.status_code == 302
    assert "evil.example.com" not in res.headers["Location"]

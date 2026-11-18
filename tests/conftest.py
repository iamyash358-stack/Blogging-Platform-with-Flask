import pytest

from app import create_app
from app.extensions import db
from app.models import Post, User
from app.utils import get_or_create_category, get_or_create_tags
from config import TestConfig


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_user(app):
    def _make(username="alice", email="alice@example.com", password="secret123"):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    return _make


@pytest.fixture()
def make_post(app):
    def _make(author, title="Hello World", body="<p>First post body</p>", category="Python", tags="flask, tips"):
        post = Post(title=title, body=body, author=author)
        post.category = get_or_create_category(category)
        post.tags = get_or_create_tags(tags)
        db.session.add(post)
        db.session.commit()
        return post
    return _make


def login(client, email="alice@example.com", password="secret123"):
    return client.post("/auth/login", data={"email": email, "password": password}, follow_redirects=True)

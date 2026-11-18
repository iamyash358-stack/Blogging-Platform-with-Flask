from app.extensions import db
from app.models import Post

from .conftest import login


def test_create_post_with_tags_and_category(client, make_user):
    make_user()
    login(client)
    res = client.post("/posts/new", data={
        "title": "My first story", "category": "Life", "tags": "Flask, python, flask",
        "body": "<p>Hello <strong>world</strong></p>",
    }, follow_redirects=True)
    assert b"Your post is live" in res.data
    post = Post.query.one()
    assert post.category.name == "Life"
    assert sorted(t.name for t in post.tags) == ["flask", "python"]  # normalised + de-duplicated


def test_empty_body_rejected(client, make_user):
    make_user()
    login(client)
    res = client.post("/posts/new", data={"title": "Empty", "body": "<p><br></p>"})
    assert b"can&#39;t be empty" in res.data
    assert Post.query.count() == 0


def test_script_tags_are_sanitised(client, make_user):
    make_user()
    login(client)
    client.post("/posts/new", data={
        "title": "XSS attempt", "body": "<p>hi</p><script>alert(1)</script><a href=\"javascript:alert(2)\">x</a>",
    })
    body = Post.query.one().body
    assert "<script>" not in body
    assert "javascript:" not in body


def test_read_post(client, make_user, make_post):
    post = make_post(make_user())
    res = client.get(f"/post/{post.id}")
    assert res.status_code == 200
    assert b"Hello World" in res.data and b"First post body" in res.data


def test_edit_own_post(client, make_user, make_post):
    post = make_post(make_user())
    login(client)
    res = client.post(f"/posts/{post.id}/edit", data={
        "title": "Updated title", "category": "Python", "tags": "x", "body": "<p>new body</p>",
    }, follow_redirects=True)
    assert b"Post updated" in res.data
    assert db.session.get(Post, post.id).title == "Updated title"


def test_cannot_edit_or_delete_others_post(client, make_user, make_post):
    owner = make_user()
    make_user("mallory", "mallory@example.com", "password123")
    post = make_post(owner)
    login(client, "mallory@example.com", "password123")
    assert client.get(f"/posts/{post.id}/edit").status_code == 403
    assert client.post(f"/posts/{post.id}/delete").status_code == 403
    assert Post.query.count() == 1


def test_delete_own_post(client, make_user, make_post):
    post = make_post(make_user())
    login(client)
    res = client.post(f"/posts/{post.id}/delete", follow_redirects=True)
    assert b"Post deleted" in res.data
    assert Post.query.count() == 0


def test_missing_post_404(client):
    assert client.get("/post/9999").status_code == 404

from app.models import Comment, Post

from .conftest import login


def test_comment_requires_login(client, make_user, make_post):
    post = make_post(make_user())
    res = client.post(f"/post/{post.id}/comment", data={"body": "Nice!"})
    assert res.status_code == 302 and "/auth/login" in res.headers["Location"]
    assert Comment.query.count() == 0


def test_authenticated_user_can_comment_and_delete(client, make_user, make_post):
    post = make_post(make_user())
    login(client)
    res = client.post(f"/post/{post.id}/comment", data={"body": "Great read"}, follow_redirects=True)
    assert b"Great read" in res.data
    comment = Comment.query.one()
    res = client.post(f"/comment/{comment.id}/delete", follow_redirects=True)
    assert Comment.query.count() == 0


def test_empty_comment_rejected(client, make_user, make_post):
    post = make_post(make_user())
    login(client)
    client.post(f"/post/{post.id}/comment", data={"body": "   "})
    assert Comment.query.count() == 0


def test_comment_is_escaped(client, make_user, make_post):
    post = make_post(make_user())
    login(client)
    client.post(f"/post/{post.id}/comment", data={"body": "<script>alert(1)</script>"})
    res = client.get(f"/post/{post.id}")
    assert b"<script>alert(1)</script>" not in res.data


def test_search_by_title_and_content(client, make_user, make_post):
    user = make_user()
    make_post(user, title="Docker deep dive", body="<p>containers</p>", tags="docker")
    make_post(user, title="Flask tips", body="<p>blueprints rock</p>", tags="flask")
    assert b"Docker deep dive" in client.get("/?q=docker").data
    assert b"Flask tips" not in client.get("/?q=docker").data
    res = client.get("/?q=blueprints")  # content search
    assert b"Flask tips" in res.data and b"Docker deep dive" not in res.data


def test_filter_by_tag_and_category(client, make_user, make_post):
    user = make_user()
    make_post(user, title="Python post", category="Python", tags="flask")
    make_post(user, title="Cooking post", category="Food", tags="recipes")
    res = client.get("/?tag=recipes")
    assert b"Cooking post" in res.data and b"Python post" not in res.data
    res = client.get("/?category=Python")
    assert b"Python post" in res.data and b"Cooking post" not in res.data


def test_pagination(client, make_user, make_post):
    user = make_user()
    for i in range(7):  # TestConfig.POSTS_PER_PAGE = 5
        make_post(user, title=f"Story number {i}")
    page1 = client.get("/").data
    page2 = client.get("/?page=2").data
    assert b"Story number 6" in page1 and b"Story number 0" not in page1
    assert b"Story number 0" in page2 and b"Story number 6" not in page2


def test_profile_page(client, make_user, make_post):
    user = make_user()
    make_post(user, title="Profile post")
    res = client.get("/user/alice")
    assert res.status_code == 200 and b"Profile post" in res.data
    assert client.get("/user/ghost").status_code == 404


def test_edit_profile_bio(client, make_user):
    make_user()
    login(client)
    res = client.post("/settings/profile", data={"bio": "I love Flask"}, follow_redirects=True)
    assert b"I love Flask" in res.data

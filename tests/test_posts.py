from typing import List
from app import schemas
import pytest # type: ignore

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    posts = [schemas.PostOut(**post) for post in res.json()]
    print(posts)
    assert res.status_code == 200
    assert len(posts) == len(test_posts)
    for post in posts:
        assert any(
            post.Post.id == test_post.id and
            post.Post.title == test_post.title and
            post.Post.content == test_post.content
            for test_post in test_posts
        )



def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401

def test_unauthorized_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_get_one_post_not_found(authorized_client, test_posts):
    res = authorized_client.get("/posts/999999")
    assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())
    assert res.status_code == 200
    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.Post.content == test_posts[0].content
    assert post.Post.owner_id == test_posts[0].owner_id

def test_create_post(authorized_client, test_user):
    post_data = {
        "title": "New Post",
        "content": "This is a new post content",
        "published": True
    }
    res = authorized_client.post("/posts/", json=post_data)
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == post_data["title"]
    assert created_post.content == post_data["content"]
    assert created_post.published == post_data["published"]
    assert created_post.owner_id == test_user['id']



def test_create_post_default_published_true(authorized_client, test_user):
    post_data = {
        "title": "New Post",
        "content": "This is a new post content"
    }
    res = authorized_client.post("/posts/", json=post_data)
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == post_data["title"]
    assert created_post.content == post_data["content"]
    assert created_post.published is True
    assert created_post.owner_id == test_user['id']


def test_unauthorized_user_create_post(client, test_user):
    post_data = {
        "title": "New Post",
        "content": "This is a new post content"
    }
    res = client.post("/posts/", json=post_data)
    assert res.status_code == 401

def test_unauthorized_user_delete_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_delete_post(authorized_client, test_posts):
    post_id = test_posts[0].id  # store before deleting
    res = authorized_client.delete(f"/posts/{post_id}")
    assert res.status_code == 204

    get_res = authorized_client.get(f"/posts/{post_id}")
    assert get_res.status_code == 404


def test_delete_post_non_existent(authorized_client):
    res = authorized_client.delete("/posts/999999")
    assert res.status_code == 404

def test_delete_other_user_post(authorized_client, test_posts, test_user):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403

def test_update_post(authorized_client, test_posts):
    post_id = test_posts[0].id
    updated_data = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }
    res = authorized_client.put(f"/posts/{post_id}", json=updated_data)
    updated_post = schemas.Post(**res.json())
    
    assert res.status_code == 200
    assert updated_post.id == post_id
    assert updated_post.title == updated_data["title"]
    assert updated_post.content == updated_data["content"]
    assert updated_post.published is False


def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    post_id = test_posts[3].id
    updated_data = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }
    res = authorized_client.put(f"/posts/{post_id}", json=updated_data)
    
    assert res.status_code == 403

def test_unauthorized_user_update_Post(client, test_user, test_posts):
    updated_data = {
    "title": "Updated Title",
    "content": "Updated Content",
    "published": False
    }
    res = client.put(f"/posts/{test_posts[0].id}", json= updated_data)
    assert res.status_code == 401
        
def test_update_post_not_found(authorized_client, test_posts):
    updated_data = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }
    res = authorized_client.put("/posts/999999", json=updated_data)
    assert res.status_code == 404



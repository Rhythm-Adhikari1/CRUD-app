from app import models
import pytest # type: ignore

@pytest.fixture()
def test_vote(test_posts, session , test_user):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user['id']) # type: ignore
    session.add(new_vote)
    session.commit()
    return new_vote  # Optional

def test_vote_on_post(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[0].id, "dir": 1})
    assert res.status_code == 201

def test_vote_twice_on_post(authorized_client, test_posts, test_vote):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    assert res.status_code == 409  # Conflict

def test_delete_vote(authorized_client, test_posts, test_vote):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    assert res.status_code == 201  # Successfully deleted vote

def test_delete_vote_non_exits(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    assert res.status_code == 404

def test_vote_post_non_exits(authorized_client, test_posts):
    res = authorized_client.post(
        "/vote/", json = {"post_id" : 80000, "dir": 1})
    assert res.status_code == 404
    
def test_vote_unauthorized_user(client, test_posts):
    res = client.post("/vote/", json={"post_id": test_posts[0].id, "dir": 1})
    assert res.status_code == 401  # Unauthorized access


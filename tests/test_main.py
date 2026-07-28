def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Wind Server API"
    assert "version" in data


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["dependencies"]["database"] == "ok"


def test_list_posts(client):
    response = client.get("/blog/posts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_post_not_found(client):
    response = client.get("/blog/posts/99999")
    assert response.status_code == 404


def test_protected_endpoint_requires_auth(client):
    response = client.get("/servers")
    assert response.status_code == 401

import app as flask_graph_app
import pytest


@pytest.fixture(autouse=True)
def clear_items():
    flask_graph_app.items.clear()
    yield
    flask_graph_app.items.clear()


@pytest.fixture
def client():
    flask_graph_app.app.config["TESTING"] = True
    return flask_graph_app.app.test_client()


def test_root_route_returns_running_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "GraphQL API is running!"


def test_graphql_playground_get_returns_html(client):
    response = client.get("/graphql")

    assert response.status_code == 200
    assert "Flask Graph API" in response.get_data(as_text=True)


def test_graphql_hello_and_goodbye_query(client):
    response = client.post("/graphql", json={"query": "{ hello goodbye }"})
    expected_hello = flask_graph_app.resolve_hello(None, None)
    expected_goodbye = flask_graph_app.resolve_goodbye(None, None)

    assert response.status_code == 200
    assert response.get_json() == {"data": {"hello": expected_hello, "goodbye": expected_goodbye}}


def test_graphql_items_starts_empty(client):
    response = client.post("/graphql", json={"query": "{ items { name quantity } }"})

    assert response.status_code == 200
    assert response.get_json() == {"data": {"items": []}}


def test_graphql_add_item_and_items_query(client):
    add_response = client.post(
        "/graphql",
        json={"query": 'mutation { addItem(name: "Oranges", quantity: 500) { name quantity } }'},
    )
    items_response = client.post("/graphql", json={"query": "{ items { name quantity } }"})

    assert add_response.status_code == 200
    assert add_response.get_json() == {"data": {"addItem": {"name": "Oranges", "quantity": 500}}}
    assert items_response.status_code == 200
    assert items_response.get_json() == {"data": {"items": [{"name": "Oranges", "quantity": 500}]}}


def test_graphql_post_returns_400_when_graphql_sync_fails(client, monkeypatch):
    expected_error = {"errors": [{"message": "forced failure"}]}

    def fake_graphql_sync(*args, **kwargs):
        return False, expected_error

    monkeypatch.setattr(flask_graph_app, "graphql_sync", fake_graphql_sync)
    response = client.post("/graphql", json={"query": "{ hello }"})

    assert response.status_code == 400
    assert response.get_json() == expected_error

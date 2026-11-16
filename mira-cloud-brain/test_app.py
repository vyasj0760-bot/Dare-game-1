import pytest

import app as mira_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("MIRA_API_TOKEN", "test-token")
    mira_app.app.config["TESTING"] = True
    return mira_app.socketio.test_client(
        mira_app.app,
        auth={"token": "test-token"},
    )


def events(client):
    return client.get_received()


def test_health_endpoint():
    response = mira_app.app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_connection_requires_token(monkeypatch):
    monkeypatch.setenv("MIRA_API_TOKEN", "test-token")
    bad_client = mira_app.socketio.test_client(
        mira_app.app,
        auth={"token": "wrong-token"},
    )
    assert not bad_client.is_connected()


def test_connection_rejects_missing_server_token(monkeypatch):
    monkeypatch.delenv("MIRA_API_TOKEN", raising=False)
    no_token_client = mira_app.socketio.test_client(
        mira_app.app,
        auth={"token": "anything"},
    )
    assert not no_token_client.is_connected()


def test_chat_message_returns_reply(client, monkeypatch):
    monkeypatch.setattr(
        mira_app,
        "generate_reply",
        lambda text: {"text": "Namaste!", "emotion": "happy"},
    )
    client.emit("chat_message", {"text": "Hello Mira"})
    received = events(client)
    assert received[-1]["name"] == "brain_reply"
    assert received[-1]["args"][0] == {"text": "Namaste!", "emotion": "happy"}


@pytest.mark.parametrize(
    "payload",
    [None, [], {}, {"text": ""}, {"text": "   "}, {"text": 123}],
)
def test_invalid_messages_are_rejected(client, payload):
    client.emit("chat_message", payload)
    received = events(client)
    assert received[-1]["name"] == "brain_error"


def test_oversized_message_is_rejected(client, monkeypatch):
    monkeypatch.setattr(
        mira_app,
        "generate_reply",
        lambda text: pytest.fail("Provider must not be called for oversized input"),
    )
    client.emit("chat_message", {"text": "x" * (mira_app.MAX_MESSAGE_CHARS + 1)})
    received = events(client)
    assert received[-1]["name"] == "brain_error"
    assert "4000" in received[-1]["args"][0]["error"]


def test_rate_limit_blocks_eleventh_message(client, monkeypatch):
    monkeypatch.setattr(
        mira_app,
        "generate_reply",
        lambda text: {"text": "ok", "emotion": "neutral"},
    )
    for _ in range(mira_app.RATE_LIMIT_MESSAGES + 1):
        client.emit("chat_message", {"text": "hello"})
    received = events(client)
    replies = [item for item in received if item["name"] == "brain_reply"]
    errors = [item for item in received if item["name"] == "brain_error"]
    assert len(replies) == mira_app.RATE_LIMIT_MESSAGES
    assert len(errors) == 1
    assert "too quickly" in errors[0]["args"][0]["error"]

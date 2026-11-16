import uuid
import pytest

import app as mira_app
import memory_store


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
    assert "memory_storage_configured" in response.get_json()


def test_connection_requires_token(monkeypatch):
    monkeypatch.setenv("MIRA_API_TOKEN", "test-token")
    bad_client = mira_app.socketio.test_client(
        mira_app.app, auth={"token": "wrong-token"}
    )
    assert not bad_client.is_connected()


def test_connection_rejects_missing_server_token(monkeypatch):
    monkeypatch.delenv("MIRA_API_TOKEN", raising=False)
    no_token_client = mira_app.socketio.test_client(
        mira_app.app, auth={"token": "anything"}
    )
    assert not no_token_client.is_connected()


def test_chat_message_returns_reply(client, monkeypatch):
    monkeypatch.setattr(
        mira_app, "generate_reply",
        lambda text, history=None: {"text": "Namaste!", "emotion": "happy"},
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
    assert events(client)[-1]["name"] == "brain_error"


def test_oversized_message_is_rejected(client, monkeypatch):
    monkeypatch.setattr(
        mira_app, "generate_reply",
        lambda *args, **kwargs: pytest.fail("Provider must not be called"),
    )
    client.emit("chat_message", {"text": "x" * (mira_app.MAX_MESSAGE_CHARS + 1)})
    received = events(client)
    assert received[-1]["name"] == "brain_error"
    assert "4000" in received[-1]["args"][0]["error"]


def test_rate_limit_blocks_eleventh_message(client, monkeypatch):
    monkeypatch.setattr(
        mira_app, "generate_reply",
        lambda text, history=None: {"text": "ok", "emotion": "neutral"},
    )
    for _ in range(mira_app.RATE_LIMIT_MESSAGES + 1):
        client.emit("chat_message", {"text": "hello"})
    received = events(client)
    assert len([e for e in received if e["name"] == "brain_reply"]) == 10
    errors = [e for e in received if e["name"] == "brain_error"]
    assert len(errors) == 1
    assert "too quickly" in errors[0]["args"][0]["error"]


def test_memory_is_opt_in_and_persists_turns(monkeypatch):
    client_id = str(uuid.uuid4())
    monkeypatch.setenv("MIRA_API_TOKEN", "test-token")
    monkeypatch.setattr(memory_store, "is_configured", lambda: True)
    saved = []
    monkeypatch.setattr(memory_store, "get_history", lambda cid, limit=10: [{"role": "user", "content": "mera naam Mayank hai"}])
    monkeypatch.setattr(memory_store, "save_turn", lambda cid, user, reply: saved.append((cid, user, reply)))
    monkeypatch.setattr(
        mira_app, "generate_reply",
        lambda text, history=None: (
            {"text": "Yaad raha!", "emotion": "happy"}
            if history and history[0]["content"] == "mera naam Mayank hai"
            else {"text": "No context", "emotion": "neutral"}
        ),
    )
    c = mira_app.socketio.test_client(
        mira_app.app,
        auth={"token": "test-token", "memory_enabled": True, "client_id": client_id},
    )
    c.emit("chat_message", {"text": "Mujhe kya yaad hai?"})
    received = c.get_received()
    reply = next(e for e in received if e["name"] == "brain_reply")
    assert reply["args"][0]["text"] == "Yaad raha!"
    assert saved == [(client_id, "Mujhe kya yaad hai?", "Yaad raha!")]


def test_memory_rejects_invalid_client_id(monkeypatch):
    monkeypatch.setenv("MIRA_API_TOKEN", "test-token")
    c = mira_app.socketio.test_client(
        mira_app.app,
        auth={"token": "test-token", "memory_enabled": True, "client_id": "not-a-uuid"},
    )
    assert not c.is_connected()


def test_clear_memory_event(monkeypatch):
    client_id = str(uuid.uuid4())
    monkeypatch.setenv("MIRA_API_TOKEN", "test-token")
    monkeypatch.setattr(memory_store, "is_configured", lambda: True)
    cleared = []
    monkeypatch.setattr(memory_store, "clear_history", lambda cid: cleared.append(cid))
    c = mira_app.socketio.test_client(
        mira_app.app,
        auth={"token": "test-token", "memory_enabled": True, "client_id": client_id},
    )
    c.emit("clear_memory")
    received = c.get_received()
    assert any(e["name"] == "memory_status" and e["args"][0].get("cleared") for e in received)
    assert cleared == [client_id]

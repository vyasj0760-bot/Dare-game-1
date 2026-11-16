import json
from unittest.mock import patch

import pytest

import brain_adapter


def test_missing_api_key_never_calls_provider(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with patch.object(brain_adapter, "urlopen") as mocked:
        with pytest.raises(brain_adapter.BrainNotIntegrated):
            brain_adapter.generate_reply("hello")
        mocked.assert_not_called()


def test_paid_model_is_blocked(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "some/paid-model")
    with patch.object(brain_adapter, "urlopen") as mocked:
        with pytest.raises(brain_adapter.BrainNotIntegrated):
            brain_adapter.generate_reply("hello")
        mocked.assert_not_called()


def test_provider_request_contains_conversation_history(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "openrouter/free")
    body = {"choices": [{"message": {"content": json.dumps({
        "text": "Namaste Mayank!", "emotion": "happy"
    })}}]}

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(body).encode()

    with patch.object(brain_adapter, "urlopen", return_value=FakeResponse()) as mocked:
        result = brain_adapter.generate_reply(
            "Mera naam yaad hai?",
            history=[{"role": "user", "content": "Mera naam Mayank hai"}],
        )
    request = mocked.call_args.args[0]
    sent = json.loads(request.data.decode())
    assert sent["model"] == "openrouter/free"
    assert sent["messages"][-2]["content"] == "Mera naam Mayank hai"
    assert result == {"text": "Namaste Mayank!", "emotion": "happy"}

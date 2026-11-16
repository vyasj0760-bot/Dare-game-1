import hmac
import os
import threading
import time
from collections import deque

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

from brain_adapter import BrainNotIntegrated, generate_reply

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)
socketio = SocketIO(app, cors_allowed_origins=[])

MAX_MESSAGE_CHARS = 4000
RATE_LIMIT_MESSAGES = 10
RATE_LIMIT_WINDOW_SECONDS = 60
_client_messages = {}
_client_messages_lock = threading.Lock()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "mira-cloud-brain-starter"}), 200


@socketio.on("connect")
def on_connect(auth=None):
    expected = os.environ.get("MIRA_API_TOKEN", "")
    supplied = auth.get("token", "") if isinstance(auth, dict) else ""
    if not expected or not isinstance(supplied, str):
        return False
    if not hmac.compare_digest(expected, supplied):
        return False


@socketio.on("disconnect")
def on_disconnect(reason=None):
    with _client_messages_lock:
        _client_messages.pop(request.sid, None)


def _over_rate_limit(client_id):
    now = time.monotonic()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    with _client_messages_lock:
        recent = _client_messages.setdefault(client_id, deque())
        while recent and recent[0] <= cutoff:
            recent.popleft()
        if len(recent) >= RATE_LIMIT_MESSAGES:
            return True
        recent.append(now)
        return False


@socketio.on("chat_message")
def on_chat_message(payload=None):
    if not request.sid:
        return

    if not isinstance(payload, dict):
        emit("brain_error", {"error": "Send a JSON object containing a text field."})
        return

    user_text = payload.get("text", "")
    if not isinstance(user_text, str) or not user_text.strip():
        emit("brain_error", {"error": "A non-empty text field is required."})
        return

    user_text = user_text.strip()
    if len(user_text) > MAX_MESSAGE_CHARS:
        emit("brain_error", {"error": f"Messages must be {MAX_MESSAGE_CHARS} characters or fewer."})
        return

    if _over_rate_limit(request.sid):
        emit("brain_error", {"error": "Mira is receiving messages too quickly. Please wait a minute."})
        return

    try:
        result = generate_reply(user_text)
        emit("brain_reply", {
            "text": result["text"],
            "emotion": result.get("emotion", "neutral"),
        })
    except BrainNotIntegrated as exc:
        emit("brain_unavailable", {"message": str(exc)})
    except Exception:
        app.logger.exception("Mira brain request failed")
        emit("brain_error", {"error": "The brain request failed. Please try again later."})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))

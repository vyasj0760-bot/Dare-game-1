import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, disconnect

from brain_adapter import BrainNotIntegrated, generate_reply

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)
socketio = SocketIO(app, cors_allowed_origins=[])


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "mira-cloud-brain-starter"}), 200


@socketio.on("connect")
def on_connect(auth=None):
    expected = os.environ.get("MIRA_API_TOKEN")
    supplied = (auth or {}).get("token") if isinstance(auth, dict) else None
    if not expected or not supplied or supplied != expected:
        return False


@socketio.on("chat_message")
def on_chat_message(payload):
    if not request.sid:
        return

    text = payload.get("text", "") if isinstance(payload, dict) else ""
    if not isinstance(text, str) or not text.strip():
        emit("brain_error", {"error": "A non-empty text field is required."})
        return

    try:
        result = generate_reply(text.strip())
        emit("brain_reply", {
            "text": result["text"],
            "emotion": result.get("emotion", "neutral"),
        })
    except BrainNotIntegrated as exc:
        emit("brain_unavailable", {"message": str(exc)})
    except Exception:
        app.logger.exception("Mira brain request failed")
        emit("brain_error", {"error": "The brain request failed."})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))

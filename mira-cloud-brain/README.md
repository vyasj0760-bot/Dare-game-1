# Mira Cloud Brain

Cloud-side chat API for the future Mira Android companion. All work is isolated
under this folder and on the `mira-cloud-brain-starter` branch.

## Implemented

- Flask + Flask-SocketIO transport and token authentication.
- Health endpoint and input validation.
- Per-connection rate guard (10 messages / 60 seconds).
- OpenRouter chat adapter using only `openrouter/free` or model IDs ending in
  `:free`; paid model IDs are rejected in code.
- Mira-specific Hindi/Hinglish persona and validated expression labels.
- Opt-in PostgreSQL chat memory with bounded recent context (last 10 turns sent
  to the model, last 40 records retained per installation).
- A `clear_memory` Socket.IO event.
- Unit tests for chat, auth, rate guard, memory opt-in, memory clearing, and
  provider request construction.

## Memory and privacy

Memory is OFF by default. To enable it, the Android client must connect with
`{ "token": "...", "memory_enabled": true, "client_id": "<stable UUID>" }`.
The UUID should be generated locally and stored privately by the app. The
server stores only recent user/assistant chat turns for that UUID. It does not
create vector embeddings or infer long-term personal facts. The client can send
`clear_memory` to delete that installation's stored turns.

A PostgreSQL database is required for memory. Set `DATABASE_URL` privately in
the hosting dashboard. Without it, chat still works but memory stays disabled.
Use a database with backups and access restricted to this service. Do not send
passwords, addresses, school details, or other sensitive information to Mira.

## Provider and cost

Set `OPENROUTER_API_KEY` privately. Keep `OPENROUTER_MODEL=openrouter/free`.
The adapter blocks non-free model IDs and contains no paid fallback. Free
models are limited and can be unavailable or rate-limited; this is a prototype
route, not unlimited production capacity. No provider request is made if the
API key is absent.

## Deploy

1. Create a Render Web Service from this repository and select branch
   `mira-cloud-brain-starter`.
2. Set Root Directory to `mira-cloud-brain`; Render can read the included
   `render.yaml`.
3. Set `MIRA_API_TOKEN` and `OPENROUTER_API_KEY` as private environment
   variables. Do not put secrets in Git.
4. For persistent memory, create a PostgreSQL database and set its private
   connection string as `DATABASE_URL`. If you skip this, memory remains off.
5. Check `/health`; it reports whether a database URL is configured, not
   whether a database login has been verified.

Have a parent/guardian review provider and hosting terms and handle any account
setup that requires an adult. Do not bypass age requirements or enable paid
usage. Avoid using personal or identifying information in tests.

## Run tests

```bash
pip install -r requirements.txt pytest
pytest -q
```

GitHub Actions runs the automated tests on changes to this folder.

## Socket.IO protocol

- Connect auth: `{ "token": "<MIRA_API_TOKEN>" }`
- Optional memory: add `"memory_enabled": true` and a stable UUID
  `"client_id"` to the auth object.
- Send: `chat_message` with `{ "text": "Hello Mira" }`
- Receive: `brain_reply` with `{ "text": "...", "emotion": "neutral" }`
- Clear stored turns: send `clear_memory`; receive `memory_status`.

## Not included

This is the cloud brain API, not the Android companion itself. Still required:
Android app, overlay permission and foreground service, animated Mira assets,
microphone/speech recognition, Hindi text-to-speech, safe on-device app actions,
and end-to-end testing on a real Android phone. OpenAmika's bridge is not a
standalone library; its host runtime and local embedding service are not present
here, so this implementation uses a small Mira-native adapter rather than
pretending the upstream bridge has been integrated. Amika's separately
licensed character, voice, and model assets are not used.

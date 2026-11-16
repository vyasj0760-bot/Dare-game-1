# Mira Cloud Brain

This is the cloud-side conversation API for the Mira Android companion. It is
isolated under `mira-cloud-brain/`; the repository's existing Dare Game files
and default `main` branch are not changed.

## Current status

- Flask + Flask-SocketIO transport
- Token authentication with constant-time comparison
- Health endpoint for hosting checks
- Per-connection message limit (10 messages per 60 seconds)
- Input validation and a 4,000-character message limit
- OpenRouter free-model adapter using the OpenAI-compatible chat completions API
- Mira's own Hindi/Hinglish system persona and a small, validated emotion label set
- Automated tests and a GitHub Actions workflow

The default model setting is `openrouter/free`, which routes to an available
free model. Free model availability and provider rate limits can change. Treat
this as a prototype/testing route, not unlimited production capacity.

## Important: no paid usage

The adapter does not contain a paid fallback. It sends requests only to the
configured OpenRouter endpoint and default free router. Never add credits or
enable paid models for this project. If the free limit is reached, Mira returns
a clear retry-later message.

## Configure

1. Deploy this folder as a Render Web Service, with Root Directory
   `mira-cloud-brain`.
2. Add `MIRA_API_TOKEN` and `OPENROUTER_API_KEY` as private environment
   variables in the hosting dashboard. Never commit real keys.
3. Keep `OPENROUTER_MODEL=openrouter/free`.
4. Check `/health` after deployment.

A parent/guardian should review provider account terms and handle any account
setup that requires an adult. Do not bypass age requirements. Avoid sending
private or identifying information to an external AI provider.

## Run tests

From this directory:

```bash
pip install -r requirements.txt pytest
pytest -q
```

GitHub Actions runs these tests when files in `mira-cloud-brain/` or its CI
workflow change.

## Socket.IO contract

Connect with auth payload `{ "token": "<MIRA_API_TOKEN>" }`.
Send event `chat_message` with `{ "text": "Hello Mira" }`.
On success the server emits `brain_reply` with
`{ "text": "...", "emotion": "neutral" }`.

The current rate limiter is in-memory and per connection. It is a basic
prototype safeguard, not a substitute for shared rate limiting when multiple
server instances are deployed.

## Not included yet

Persistent memory, speech recognition, Hindi text-to-speech, animated
character assets, Android overlay/foreground service, app controls, durable
rate limiting, and end-to-end Android testing still need to be built.
OpenAmika's separately licensed character, voice, and model assets are not used.

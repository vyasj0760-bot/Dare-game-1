# Mira Cloud Brain

This is the cloud-side conversation API for the Mira Android companion. It is
isolated under `mira-cloud-brain/`; the repository's existing Dare Game files
and default `main` branch are not changed.

## Current status

- Flask + Flask-SocketIO transport
- Token authentication for Socket.IO connections
- Health endpoint for hosting checks
- **OpenRouter free-model adapter** using the OpenAI-compatible chat completions API
- Mira's own Hindi/Hinglish system persona and a small, validated emotion label set

The default model setting is `openrouter/free`, which routes to an available
free model. Free model availability and provider rate limits can change. The
current free account allowance is limited (currently 50 requests/day for
free variants); this is for testing, not unlimited production use.

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

## Socket.IO contract

Connect with auth payload `{ "token": "<MIRA_API_TOKEN>" }`.
Send event `chat_message` with `{ "text": "Hello Mira" }`.
On success the server emits `brain_reply` with
`{ "text": "...", "emotion": "neutral" }`.

## Not included yet

This is a first cloud chat adapter, not the complete Mira app. Persistent
memory, speech recognition, Hindi text-to-speech, animated character assets,
Android overlay/foreground service, app controls, rate limiting, and end-to-end
Android testing still need to be built. OpenAmika's separately licensed
character, voice, and model assets are not used.

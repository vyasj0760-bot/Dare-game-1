# Mira Cloud Brain (starter)

This folder is an isolated starter for Mira's cloud-side conversation service. It does not alter the existing Dare Game Android/WebView app.

## Current status

- Flask + Flask-SocketIO transport scaffold
- Bearer-token authentication for Socket.IO connections
- Health endpoint for hosting checks
- Explicit brain adapter boundary for integrating OpenAmika's reusable orchestration/persona/memory modules

**Not yet a working AI brain:** `brain_adapter.py` is intentionally a placeholder. No LLM, memory database, TTS, speech recognition, or Android overlay is included yet. The next integration step is to adapt the compatible OpenAmika brain modules and connect a provider such as OpenRouter. Do not copy Amika's separately licensed artwork, voice, or model assets.

## Deploy (Render)

1. Create a Render Web Service connected to this GitHub repository.
2. Set the Root Directory to `mira-cloud-brain`.
3. Use the included `render.yaml` or configure the build/start commands from it.
4. Add environment variables from `.env.example` in Render's dashboard. Generate a long random `MIRA_API_TOKEN`; add an LLM provider key only when the adapter is implemented.
5. Deploy and check `/health`.

The free service may sleep when idle, so the first request can be delayed. Free hosting does not mean LLM API usage is free. Keep provider keys private and configure provider-side spending limits.

## Socket.IO contract

Connect with auth payload `{ "token": "<MIRA_API_TOKEN>" }`.

Send event `chat_message` with `{ "text": "Hello Mira" }`.

On successful integration, the server will emit `brain_reply` with `{ "text": "...", "emotion": "neutral" }`. Until then it emits `brain_unavailable` rather than pretending a scripted reply is AI.

## Security notes

- Never commit real API keys or tokens.
- Use HTTPS in production.
- Keep Android permissions and device actions on the Android side, with user confirmation for consequential actions.
- Add rate limiting and persistent storage before public release.

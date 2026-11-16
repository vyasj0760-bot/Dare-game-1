"""Free-tier OpenRouter adapter for Mira.

The API key is read only from the server environment. No paid fallback is used.
"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class BrainNotIntegrated(RuntimeError):
    """Raised when the provider is not configured or cannot serve a reply."""


SYSTEM_PROMPT = """You are Mira, a friendly 2D anime-style AI companion.
Speak naturally in Hindi/Hinglish unless the user uses another language.
Be warm, curious, playful, and respectful. Never claim to be human or to
control the user's phone. Do not encourage emotional dependence, secrecy,
unsafe actions, or sharing passwords, addresses, or private information.
For phone actions, explain the suggested action; the Android app must request
the user's confirmation and perform it locally.
Return ONLY a JSON object with exactly two keys:
"text": your concise conversational reply,
"emotion": one of neutral, happy, curious, confused, sleepy, or thoughtful.
Do not include markdown fences or extra keys."""


def _normalise_result(content: str) -> dict:
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict) and isinstance(parsed.get("text"), str):
            emotion = parsed.get("emotion", "neutral")
            allowed = {"neutral", "happy", "curious", "confused", "sleepy", "thoughtful"}
            return {
                "text": parsed["text"].strip() or "Ek second, mujhe dobara try karne do.",
                "emotion": emotion if emotion in allowed else "neutral",
            }
    except (json.JSONDecodeError, TypeError):
        pass
    return {"text": content.strip(), "emotion": "neutral"}


def generate_reply(user_text: str, history=None) -> dict:
    """Generate a reply; history is a bounded list of prior chat turns."""
    if not isinstance(user_text, str) or not user_text.strip():
        raise ValueError("user_text must not be empty")

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise BrainNotIntegrated(
            "Mira's free AI provider is not configured yet. No paid service was called."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if isinstance(history, list):
        for item in history[-10:]:
            if (
                isinstance(item, dict)
                and item.get("role") in {"user", "assistant"}
                and isinstance(item.get("content"), str)
                and item["content"].strip()
            ):
                messages.append({
                    "role": item["role"],
                    "content": item["content"][:4000],
                })
    messages.append({"role": "user", "content": user_text.strip()})

    model = os.environ.get("OPENROUTER_MODEL", "openrouter/free").strip()
    if model != "openrouter/free" and not model.endswith(":free"):
        raise BrainNotIntegrated("Mira is configured for free models only. Paid model IDs are blocked.")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_SITE_URL", "https://example.com"),
        "X-Title": os.environ.get("OPENROUTER_APP_NAME", "Mira Companion"),
    }
    request = Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise BrainNotIntegrated("The AI provider rejected its server key. Check the private deployment settings.") from exc
        if exc.code == 429:
            raise BrainNotIntegrated("Mira has reached the free provider's usage limit. Please try later.") from exc
        raise BrainNotIntegrated(f"The AI provider is temporarily unavailable (HTTP {exc.code}).") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise BrainNotIntegrated("Mira could not reach the free AI provider. Please try again later.") from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise BrainNotIntegrated("The AI provider returned an unexpected response.") from exc

    if not isinstance(content, str) or not content.strip():
        raise BrainNotIntegrated("The AI provider returned an empty response.")
    return _normalise_result(content)

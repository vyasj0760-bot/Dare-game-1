"""Adapter boundary for the OpenAmika brain integration.

This starter deliberately does not return canned responses. Replace this
placeholder with a thin adapter around the compatible OpenAmika orchestration,
persona, and memory modules after reviewing their current license/notices.
"""


class BrainNotIntegrated(RuntimeError):
    """Raised while the real LLM-backed brain has not been connected."""


def generate_reply(user_text: str) -> dict:
    """Return {text, emotion} after the real brain is integrated."""
    if not user_text or not user_text.strip():
        raise ValueError("user_text must not be empty")

    raise BrainNotIntegrated(
        "Mira's AI brain is not integrated yet. This is a transport starter only."
    )

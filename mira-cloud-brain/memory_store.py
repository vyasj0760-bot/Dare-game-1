"""Opt-in PostgreSQL conversation memory for Mira.

This stores recent chat turns only. It is not semantic/vector memory.
Memory is disabled unless the client explicitly enables it at Socket.IO connect.
"""
import os
from urllib.parse import urlparse, urlunparse


def is_configured() -> bool:
    return bool(os.environ.get("DATABASE_URL", "").strip())


def _connect():
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("PostgreSQL driver is not installed") from exc

    url = os.environ.get("DATABASE_URL", "").strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return psycopg.connect(url, connect_timeout=8)


def _ensure_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mira_chat_turns (
            id BIGSERIAL PRIMARY KEY,
            client_id UUID NOT NULL,
            role VARCHAR(16) NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS mira_chat_turns_client_id_id_idx
        ON mira_chat_turns (client_id, id DESC)
    """)


def get_history(client_id: str, limit: int = 10) -> list:
    if not is_configured():
        return []
    limit = max(1, min(int(limit), 20))
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """SELECT role, content FROM (
                   SELECT id, role, content FROM mira_chat_turns
                   WHERE client_id = %s ORDER BY id DESC LIMIT %s
               ) recent ORDER BY id ASC""",
            (client_id, limit),
        ).fetchall()
    return [{"role": row[0], "content": row[1]} for row in rows]


def save_turn(client_id: str, user_text: str, assistant_text: str) -> None:
    if not is_configured():
        return
    with _connect() as conn:
        _ensure_schema(conn)
        conn.execute(
            "INSERT INTO mira_chat_turns (client_id, role, content) VALUES (%s, 'user', %s)",
            (client_id, user_text),
        )
        conn.execute(
            "INSERT INTO mira_chat_turns (client_id, role, content) VALUES (%s, 'assistant', %s)",
            (client_id, assistant_text),
        )
        # Keep a bounded recent history rather than storing an unlimited transcript.
        conn.execute(
            """DELETE FROM mira_chat_turns
               WHERE client_id = %s AND id NOT IN (
                   SELECT id FROM mira_chat_turns
                   WHERE client_id = %s ORDER BY id DESC LIMIT 40
               )""",
            (client_id, client_id),
        )


def clear_history(client_id: str) -> None:
    if not is_configured():
        return
    with _connect() as conn:
        _ensure_schema(conn)
        conn.execute("DELETE FROM mira_chat_turns WHERE client_id = %s", (client_id,))

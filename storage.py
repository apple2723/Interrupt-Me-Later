from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATA_FILE = (
    Path(__file__).parent
    / "data"
    / "sessions.json"
)


def ensure_data_file() -> None:
    DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not DATA_FILE.exists():
        DATA_FILE.write_text(
            "[]",
            encoding="utf-8",
        )


def load_sessions() -> list[dict[str, Any]]:
    ensure_data_file()

    try:
        data = json.loads(
            DATA_FILE.read_text(
                encoding="utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return []

    if isinstance(data, list):
        return data

    return []


def save_sessions(
    sessions: list[dict[str, Any]],
) -> None:
    ensure_data_file()

    DATA_FILE.write_text(
        json.dumps(
            sessions,
            indent=2,
        ),
        encoding="utf-8",
    )


def add_session(
    session: dict[str, Any],
) -> None:
    sessions = load_sessions()

    sessions.insert(
        0,
        session,
    )

    save_sessions(sessions)


def delete_session(
    session_id: str,
) -> None:
    sessions = load_sessions()

    remaining_sessions = [
        session
        for session in sessions
        if session.get("id") != session_id
    ]

    save_sessions(
        remaining_sessions
    )
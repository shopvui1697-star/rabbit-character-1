"""Session store interface and in-memory implementation.

Phase 1: In-memory only.
Phase 4: Add Redis implementation for production persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.session import SessionState


class SessionStore(ABC):
    """Abstract session store interface."""

    @abstractmethod
    async def get(self, session_id: str) -> SessionState | None:
        """Retrieve a session by ID. Returns None if not found."""
        ...

    @abstractmethod
    async def save(self, session_id: str, state: SessionState) -> None:
        """Persist a session state."""
        ...

    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """Delete a session."""
        ...


class InMemorySessionStore(SessionStore):
    """Simple in-memory session store for development."""

    def __init__(self) -> None:
        self._store: dict[str, SessionState] = {}

    async def get(self, session_id: str) -> SessionState | None:
        return self._store.get(session_id)

    async def save(self, session_id: str, state: SessionState) -> None:
        self._store[session_id] = state

    async def delete(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def list_sessions(self) -> list[str]:
        """List all active session IDs (dev helper)."""
        return list(self._store.keys())

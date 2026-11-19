"""Facts about one container, gathered by plain code (no AI involved)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MAX_LOG_LINES = 50


@dataclass(frozen=True)
class Bundle:
    """Everything the classifier knows about a container.

    Build it by hand in tests, or from `docker inspect` output with
    `Bundle.from_inspect`.
    """

    name: str
    status: str  # running, exited, restarting, created, paused, dead, ...
    exit_code: int | None = None
    oom_killed: bool = False
    restart_count: int = 0
    health: str | None = None  # healthy | unhealthy | starting | None (no healthcheck)
    error: str = ""  # State.Error from docker (e.g. port allocation failures)
    logs: tuple[str, ...] = ()  # most recent lines, oldest first

    @classmethod
    def from_inspect(
        cls, inspect: dict[str, Any] | list[dict[str, Any]], logs: str | list[str] = ""
    ) -> "Bundle":
        """Build a Bundle from `docker inspect <name>` JSON plus log text."""
        if isinstance(inspect, list):
            if not inspect:
                raise ValueError("empty docker inspect output")
            inspect = inspect[0]

        state = inspect.get("State") or {}
        if isinstance(logs, str):
            logs = logs.splitlines()
        lines = tuple(line.rstrip() for line in logs if line.strip())[-MAX_LOG_LINES:]

        return cls(
            name=(inspect.get("Name") or str(inspect.get("Id", ""))[:12]).lstrip("/"),
            status=str(state.get("Status") or "unknown").lower(),
            exit_code=state.get("ExitCode"),
            oom_killed=bool(state.get("OOMKilled")),
            restart_count=int(inspect.get("RestartCount") or 0),
            health=(state.get("Health") or {}).get("Status"),
            error=state.get("Error") or "",
            logs=lines,
        )

"""Configuration loading without third-party dotenv dependencies."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines without replacing already-defined environment values."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def find_repo_env(start: Path) -> Path | None:
    """Find the nearest .env while walking toward the filesystem root."""
    current = start.resolve()
    for directory in (current, *current.parents):
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str = "openrouter/free"
    base_url: str = "https://openrouter.ai/api/v1"
    max_steps: int = 12
    timeout_seconds: int = 90
    max_output_chars: int = 20_000

    @classmethod
    def from_environment(cls, start: Path | None = None) -> "Settings":
        env_path = find_repo_env(start or Path.cwd())
        if env_path:
            load_env_file(env_path)
        raw_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if raw_key.lower() in {"", "replace-with-your-openrouter-key"}:
            raw_key = ""
        return cls(
            api_key=raw_key or None,
            model=os.getenv("OPENROUTER_MODEL", "openrouter/free").strip() or "openrouter/free",
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/"),
            max_steps=max(1, int(os.getenv("HARNESS_MAX_STEPS", "12"))),
        )

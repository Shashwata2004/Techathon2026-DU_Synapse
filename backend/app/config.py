import os
from dataclasses import dataclass
from datetime import time

from dotenv import load_dotenv


load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _time_env(name: str, default: str) -> time:
    raw = os.getenv(name, default)
    hour, minute = raw.split(":", maxsplit=1)
    return time(hour=int(hour), minute=int(minute))


@dataclass(frozen=True)
class Settings:
    backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port: int = _int_env("BACKEND_PORT", 8000)
    simulation_enabled: bool = _bool_env("SIMULATION_ENABLED", True)
    simulation_interval_seconds: int = _int_env("SIMULATION_INTERVAL_SECONDS", 25)
    office_hours_start: time = _time_env("OFFICE_HOURS_START", "09:00")
    office_hours_end: time = _time_env("OFFICE_HOURS_END", "17:00")
    cors_allow_origins: tuple[str, ...] = ("*",)


settings = Settings()

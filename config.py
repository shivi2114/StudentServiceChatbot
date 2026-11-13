import os
from pathlib import Path


def _load_env_file():
    """Load key-value pairs from .env into os.environ if not already set."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.is_file():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass


_load_env_file()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()


def has_groq_api_key() -> bool:
    """Return True if a non-empty Groq API key is configured."""
    return bool(GROQ_API_KEY)

import os
from pathlib import Path

# Resolve base directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent

# Read .env file from root or backend dir
def load_env_vars():
    for env_path in [ROOT_DIR / ".env", BACKEND_DIR / ".env"]:
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

load_env_vars()

class Settings:
    PROJECT_NAME: str = "CampusAI - Student Assistance System"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Security / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "campusai-secret-key-production-grade-2026-secure-token")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # Database
    # Defaults to SQLite for immediate local plug-and-play; can be overridden by PostgreSQL URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{ROOT_DIR / 'campusai.db'}"
    )
    
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()
    
    # Vector DB / Chroma
    CHROMA_DIR: Path = ROOT_DIR / "chroma_db"
    DOCUMENTS_DIR: Path = ROOT_DIR / "documents"

settings = Settings()

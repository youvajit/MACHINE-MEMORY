import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    DATABASE = BASE_DIR / "instance" / "machine_memory.sqlite3"
    ALLOWED_EXTENSIONS = {"wav"}
    SAMPLE_RATE = 22050
    MAX_AUDIO_SECONDS = 30

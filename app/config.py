import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Database Connection URL (Supabase/PostgreSQL)
# Supports standard DATABASE_URL or SUPABASE_DB_URL, with a fallback for local development (SQLite)
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL") or "sqlite:///./tupinamba.db"

# Base configuration for authentication/session security
SECRET_KEY = os.getenv("SECRET_KEY", "olorokebirigui_secret_key_89231")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

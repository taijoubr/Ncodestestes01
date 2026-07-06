from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

# Handle Supabase connection details gracefully
# If DATABASE_URL starts with postgres://, replace with postgresql:// for SQLAlchemy compatibility
db_url = DATABASE_URL
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# SQLite specific check
is_sqlite = db_url.startswith("sqlite")

connect_args = {}
if is_sqlite:
    connect_args = {"check_same_thread": False}

# Create engine with pre-ping enabled to ensure connection stability with remote DBs (like Supabase)
engine = create_engine(
    db_url,
    pool_pre_ping=True,
    connect_args=connect_args,
    **({} if is_sqlite else {"pool_recycle": 3600})
)

# SessionLocal class will be used for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()

# Dependency to get db session in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

# Handle database connection details gracefully
# If DATABASE_URL starts with postgres://, replace with postgresql:// for SQLAlchemy compatibility
db_url = DATABASE_URL
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# SQLite specific check
is_sqlite = db_url.startswith("sqlite")

connect_args = {}
if is_sqlite:
    connect_args = {"check_same_thread": False}

# Create engine with pre-ping and timeout settings to ensure connection stability and prevent hangs on Vercel
try:
    if not is_sqlite:
        connect_args["connect_timeout"] = 5  # 5 seconds timeout for remote PostgreSQL/Supabase
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args=connect_args,
        **({} if is_sqlite else {"pool_recycle": 3600})
    )
except Exception as e:
    print(f"Warning: Failed to create engine for {db_url}: {e}. Falling back to SQLite...")
    fallback_url = "sqlite:////tmp/tupinamba.db"
    engine = create_engine(
        fallback_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )

# SessionLocal class will be used for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()

# Dependency to get db session in routes
def get_db():
    try:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        print(f"Database session error: {e}. Attempting fallback SQLite session...")
        fallback_engine = create_engine("sqlite:////tmp/tupinamba.db", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=fallback_engine)
        FallbackSession = sessionmaker(autocommit=False, autoflush=False, bind=fallback_engine)
        db = FallbackSession()
        try:
            yield db
        finally:
            db.close()


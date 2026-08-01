from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
import time

from app.database import engine, Base

GLOBAL_LOGO_CACHE = None
GLOBAL_LOGO_VERSION = str(int(time.time()))

def detect_image_mime(raw_bytes: bytes, fallback_mime: str = "image/png") -> str:
    if not raw_bytes:
        return fallback_mime or "image/png"
    header = raw_bytes[:100]
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    elif header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    elif header.startswith(b"RIFF") and b"WEBP" in header[:20]:
        return "image/webp"
    elif header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return "image/gif"
    elif b"<svg" in header.lower() or b"<?xml" in header.lower():
        return "image/svg+xml"
    return fallback_mime or "image/png"

def get_logo_version():
    global GLOBAL_LOGO_CACHE, GLOBAL_LOGO_VERSION
    if GLOBAL_LOGO_CACHE is not None and "version" in GLOBAL_LOGO_CACHE:
        return GLOBAL_LOGO_CACHE["version"]
    get_logo_bytes()
    if GLOBAL_LOGO_CACHE is not None and "version" in GLOBAL_LOGO_CACHE:
        return GLOBAL_LOGO_CACHE["version"]
    return str(GLOBAL_LOGO_VERSION)

from app.routes import router

# Define FastAPI application with metadata
app = FastAPI(
    title="Oloroke Birigui",
    description="Site Oficial do Oloroke Birigui - Paz, Espiritualidade e Caridade.",
    version="1.0.0"
)

# Add Session Middleware for secure cookie-based admin sessions
app.add_middleware(
    SessionMiddleware,
    secret_key="Oloroke_Admin_Secret_Key_2026_Secure!",
    session_cookie="oloroke_admin_session",
    max_age=18000, # 5 hours session lifetime
    same_site="lax",
    https_only=False,
)

# Mount static files (images, css, icons)
# Ensure the static directory exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    os.makedirs(os.path.join(BASE_DIR, "static/css"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "static/images"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "static/icons"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "static/fonts"), exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create static directories (read-only filesystem): {e}")

from fastapi.responses import FileResponse, Response

def set_global_logo_cache(raw_bytes: bytes, mime_type: str = "image/png"):
    global GLOBAL_LOGO_CACHE, GLOBAL_LOGO_VERSION
    import hashlib
    real_mime = detect_image_mime(raw_bytes, mime_type)
    ver_str = hashlib.md5(raw_bytes).hexdigest()[:10]
    
    GLOBAL_LOGO_CACHE = {
        "bytes": raw_bytes,
        "mime": real_mime,
        "version": ver_str
    }
    GLOBAL_LOGO_VERSION = ver_str

    tmp_path = "/tmp/logo.png"
    try:
        with open(tmp_path, "wb") as f:
            f.write(raw_bytes)
    except Exception:
        pass

    try:
        static_dir = os.path.join(BASE_DIR, "static/images")
        os.makedirs(static_dir, exist_ok=True)
        with open(os.path.join(static_dir, "logo.png"), "wb") as f:
            f.write(raw_bytes)
        import base64
        import json
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        with open(os.path.join(static_dir, "logo_b64.json"), "w") as f:
            json.dump({"b64": b64_str, "mime": real_mime, "version": ver_str}, f)
    except Exception as ex:
        print(f"Notice saving logo static file: {ex}")

def get_logo_bytes():
    global GLOBAL_LOGO_CACHE, GLOBAL_LOGO_VERSION
    if GLOBAL_LOGO_CACHE is not None and GLOBAL_LOGO_CACHE.get("bytes"):
        return GLOBAL_LOGO_CACHE["bytes"], GLOBAL_LOGO_CACHE["mime"]

    import base64
    import hashlib

    # 1. Check SQLite database FIRST (Source of truth for user config)
    try:
        from app.database import SessionLocal
        from app.models import ConfiguracaoSistema
        db = SessionLocal()
        try:
            cfg_b64 = db.query(ConfiguracaoSistema).filter(ConfiguracaoSistema.chave == "logo_b64").first()
            cfg_mime = db.query(ConfiguracaoSistema).filter(ConfiguracaoSistema.chave == "logo_mime").first()
            if cfg_b64 and cfg_b64.valor:
                raw_bytes = base64.b64decode(cfg_b64.valor)
                stored_mime = cfg_mime.valor if cfg_mime and cfg_mime.valor else "image/png"
                real_mime = detect_image_mime(raw_bytes, stored_mime)
                ver_str = hashlib.md5(raw_bytes).hexdigest()[:10]
                
                GLOBAL_LOGO_CACHE = {"bytes": raw_bytes, "mime": real_mime, "version": ver_str}
                GLOBAL_LOGO_VERSION = ver_str
                
                try:
                    with open("/tmp/logo.png", "wb") as f:
                        f.write(raw_bytes)
                except Exception:
                    pass
                return raw_bytes, real_mime
        finally:
            db.close()
    except Exception as ex:
        print(f"Error fetching logo from SQLite: {ex}")

    # 2. Check Firestore
    try:
        from app.firebase_config import get_firestore_client
        db_fs = get_firestore_client()
        if db_fs:
            doc = db_fs.collection("configuracoes").document("logo_data").get()
            if doc.exists:
                data_dict = doc.to_dict()
                b64_str = data_dict.get("logo_b64")
                stored_mime = data_dict.get("mime_type", "image/png")
                if b64_str:
                    raw_bytes = base64.b64decode(b64_str)
                    real_mime = detect_image_mime(raw_bytes, stored_mime)
                    ver_str = hashlib.md5(raw_bytes).hexdigest()[:10]
                    GLOBAL_LOGO_CACHE = {"bytes": raw_bytes, "mime": real_mime, "version": ver_str}
                    GLOBAL_LOGO_VERSION = ver_str
                    
                    # Sync to SQLite
                    try:
                        from app.database import SessionLocal
                        from app.models import ConfiguracaoSistema
                        db_sql = SessionLocal()
                        c_b64 = db_sql.query(ConfiguracaoSistema).filter(ConfiguracaoSistema.chave == "logo_b64").first()
                        if not c_b64:
                            db_sql.add(ConfiguracaoSistema(chave="logo_b64", valor=b64_str))
                        else:
                            c_b64.valor = b64_str
                        c_mime = db_sql.query(ConfiguracaoSistema).filter(ConfiguracaoSistema.chave == "logo_mime").first()
                        if not c_mime:
                            db_sql.add(ConfiguracaoSistema(chave="logo_mime", valor=real_mime))
                        else:
                            c_mime.valor = real_mime
                        db_sql.commit()
                        db_sql.close()
                    except Exception:
                        pass
                    return raw_bytes, real_mime
    except Exception as ex:
        print(f"Error serving custom logo from Firestore: {ex}")

    # 3. Check local static/images/logo_b64.json file backup
    try:
        json_path = os.path.join(BASE_DIR, "static/images/logo_b64.json")
        if os.path.exists(json_path):
            import json
            with open(json_path, "r") as f:
                data = json.load(f)
            if data and "b64" in data:
                raw_bytes = base64.b64decode(data["b64"])
                real_mime = detect_image_mime(raw_bytes, data.get("mime", "image/png"))
                ver_str = hashlib.md5(raw_bytes).hexdigest()[:10]
                GLOBAL_LOGO_CACHE = {"bytes": raw_bytes, "mime": real_mime, "version": ver_str}
                GLOBAL_LOGO_VERSION = ver_str
                return raw_bytes, real_mime
    except Exception as ex:
        print(f"Error reading logo_b64.json: {ex}")

    # 4. Check /tmp/logo.png
    tmp_path = "/tmp/logo.png"
    if os.path.exists(tmp_path):
        try:
            with open(tmp_path, "rb") as f:
                raw_bytes = f.read()
            if raw_bytes:
                real_mime = detect_image_mime(raw_bytes, "image/png")
                ver_str = hashlib.md5(raw_bytes).hexdigest()[:10]
                GLOBAL_LOGO_CACHE = {"bytes": raw_bytes, "mime": real_mime, "version": ver_str}
                GLOBAL_LOGO_VERSION = ver_str
                return raw_bytes, real_mime
        except Exception:
            pass

    # 5. Fallback to default static file static/images/logo.png
    path = os.path.join(BASE_DIR, "static/images/logo.png")
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                raw_bytes = f.read()
            if raw_bytes:
                real_mime = detect_image_mime(raw_bytes, "image/png")
                ver_str = hashlib.md5(raw_bytes).hexdigest()[:10]
                GLOBAL_LOGO_CACHE = {"bytes": raw_bytes, "mime": real_mime, "version": ver_str}
                GLOBAL_LOGO_VERSION = ver_str
                return raw_bytes, real_mime
        except Exception:
            pass

    return b"", "image/png"

@app.get("/logo.png")
@app.get("/static/images/logo.png")
async def serve_logo_png():
    raw_bytes, mime_type = get_logo_bytes()
    if raw_bytes:
        return Response(
            content=raw_bytes,
            media_type=mime_type,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    fallback_path = os.path.join(BASE_DIR, "static/images/logo.png")
    if os.path.exists(fallback_path):
        try:
            with open(fallback_path, "rb") as f:
                fb_bytes = f.read()
            fb_mime = detect_image_mime(fb_bytes, "image/png")
            return Response(
                content=fb_bytes,
                media_type=fb_mime,
                headers={"Cache-Control": "no-cache, must-revalidate"}
            )
        except Exception:
            return FileResponse(fallback_path)
    return Response(status_code=404)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Include the main routing module
app.include_router(router)

def seed_initial_data():
    from app.database import SessionLocal, engine
    from app.models import User, Aviso, AgendaEvent, QuadroAviso, Membro, ConfiguracaoSistema
    from app.auth_utils import hash_password
    import datetime
    from sqlalchemy import text

    db = SessionLocal()
    try:
        # Check and add role column if not exists
        try:
            db.execute(text("SELECT role FROM users LIMIT 1"))
        except Exception:
            db.rollback()
            try:
                db.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'secretario'"))
                db.commit()
                print("Role column added to users table successfully!")
            except Exception as ex:
                print(f"Failed to add role column: {ex}")
                db.rollback()

        # Check and add publico and segmento columns to agenda_events table if not exist
        try:
            db.execute(text("SELECT publico FROM agenda_events LIMIT 1"))
        except Exception:
            db.rollback()
            try:
                db.execute(text("ALTER TABLE agenda_events ADD COLUMN publico BOOLEAN DEFAULT 1"))
                db.commit()
                print("Column publico added to agenda_events table successfully!")
            except Exception as ex:
                print(f"Failed to add column publico: {ex}")
                db.rollback()

        try:
            db.execute(text("SELECT segmento FROM agenda_events LIMIT 1"))
        except Exception:
            db.rollback()
            try:
                db.execute(text("ALTER TABLE agenda_events ADD COLUMN segmento VARCHAR(50) DEFAULT 'Umbanda'"))
                db.commit()
                print("Column segmento added to agenda_events table successfully!")
            except Exception as ex:
                print(f"Failed to add column segmento: {ex}")
                db.rollback()

        # Check and add valor_mensalidade column to membros table if not exists
        try:
            db.execute(text("SELECT valor_mensalidade FROM membros LIMIT 1"))
        except Exception:
            db.rollback()
            try:
                db.execute(text("ALTER TABLE membros ADD COLUMN valor_mensalidade FLOAT DEFAULT 50.0"))
                db.commit()
                print("Column valor_mensalidade added to membros table successfully!")
            except Exception as ex:
                print(f"Failed to add column valor_mensalidade: {ex}")
                db.rollback()

        # Check and add aprovado_consulta_privada, valor_consulta and isento_mensalidade columns to membros table
        for col, col_type in [
            ("aprovado_consulta_privada", "BOOLEAN DEFAULT 0"),
            ("valor_consulta", "FLOAT DEFAULT 0.0"),
            ("isento_mensalidade", "BOOLEAN DEFAULT 0")
        ]:
            try:
                db.execute(text(f"SELECT {col} FROM membros LIMIT 1"))
            except Exception:
                db.rollback()
                try:
                    db.execute(text(f"ALTER TABLE membros ADD COLUMN {col} {col_type}"))
                    db.commit()
                    print(f"Column {col} added to membros table successfully!")
                except Exception as ex:
                    print(f"Failed to add column {col} to membros: {ex}")
                    db.rollback()

        # Check and add tipo column to consultas_privadas table if not exists
        try:
            db.execute(text("SELECT tipo FROM consultas_privadas LIMIT 1"))
        except Exception:
            db.rollback()
            try:
                db.execute(text("ALTER TABLE consultas_privadas ADD COLUMN tipo VARCHAR(50) DEFAULT 'Consulta'"))
                db.commit()
                print("Column tipo added to consultas_privadas table successfully!")
            except Exception as ex:
                print(f"Failed to add column tipo to consultas_privadas: {ex}")
                db.rollback()

        # Check and add valor_consulta column to consultas_privadas table if not exists
        try:
            db.execute(text("SELECT valor_consulta FROM consultas_privadas LIMIT 1"))
        except Exception:
            db.rollback()
            try:
                db.execute(text("ALTER TABLE consultas_privadas ADD COLUMN valor_consulta FLOAT DEFAULT 0.0"))
                db.commit()
                print("Column valor_consulta added to consultas_privadas table successfully!")
            except Exception as ex:
                print(f"Failed to add column valor_consulta to consultas_privadas: {ex}")
                db.rollback()

        # Check and add new columns for member registration
        for col, col_type in [
            ("full_name", "VARCHAR(150)"),
            ("phone", "VARCHAR(30)"),
            ("birth_date", "DATE"),
            ("is_approved", "BOOLEAN DEFAULT 1")
        ]:
            try:
                db.execute(text(f"SELECT {col} FROM users LIMIT 1"))
            except Exception:
                db.rollback()
                try:
                    db.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_type}"))
                    db.commit()
                    print(f"Column {col} added to users table successfully!")
                except Exception as ex:
                    print(f"Failed to add column {col}: {ex}")
                    db.rollback()

        # 1. Seed admin user if not exists, and ensure correct password
        has_admin = db.query(User).filter(User.is_admin == True).first()
        if not has_admin:
            print("Creating default admin user...")
            hashed = hash_password("taijou123")
            admin_user = User(
                username="programador",
                email="programador@olorokebirigui.org",
                hashed_password=hashed,
                is_active=True,
                is_admin=True,
                role="programador"
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully! (Username: programador, Password: taijou123)")
        else:
            # Ensure existing admins have a role assigned
            admins = db.query(User).filter(User.is_admin == True).all()
            for adm in admins:
                if adm.username == "programador":
                    adm.role = "programador"
                elif adm.username == "admin":
                    adm.role = "programador"
                elif not adm.role:
                    adm.role = "secretario"
            db.commit()

        # Ensure 'Ricardo' user exists as pai_de_santo
        ricardo_user = db.query(User).filter(User.username == "Ricardo").first()
        if not ricardo_user:
            print("Creating Ricardo user (Pai de Santo)...")
            hashed_ricardo = hash_password("Ricardo123")
            ricardo_user = User(
                username="Ricardo",
                email="ricardo@olorokebirigui.org",
                hashed_password=hashed_ricardo,
                is_active=True,
                is_admin=True,
                role="pai_de_santo"
            )
            db.add(ricardo_user)
            db.commit()
            print("Ricardo user (Pai de Santo) created successfully!")
        else:
            # Keep role and admin status verified
            ricardo_user.role = "pai_de_santo"
            ricardo_user.is_admin = True
            db.commit()

        # Ensure active Membro record for Ricardo (Pai de Santo)
        ricardo_membro = db.query(Membro).filter(Membro.email == "ricardo@olorokebirigui.org").first()
        if not ricardo_membro:
            print("Seeding Ricardo as Membro...")
            new_ric_membro = Membro(
                nome="Pai Ricardo",
                cargo="Pai de Santo",
                telefone="(11) 99999-8888",
                email="ricardo@olorokebirigui.org",
                ativo=True,
                valor_mensalidade=0.0,
                aprovado_consulta_privada=True,
                valor_consulta=100.0
            )
            db.add(new_ric_membro)
            db.commit()
            print("Ricardo seeded as Membro successfully!")
        else:
            ricardo_membro.ativo = True
            ricardo_membro.aprovado_consulta_privada = True
            if not ricardo_membro.valor_consulta or ricardo_membro.valor_consulta == 0:
                ricardo_membro.valor_consulta = 100.0
            db.commit()

        # Ensure 'Aline' user exists as tesoureiro
        aline_user = db.query(User).filter(User.username == "Aline").first()
        if not aline_user:
            print("Creating Aline user (Tesoureiro)...")
            hashed_aline = hash_password("aline123")
            aline_user = User(
                username="Aline",
                email="aline@olorokebirigui.org",
                hashed_password=hashed_aline,
                is_active=True,
                is_admin=True,
                role="tesoureiro"
            )
            db.add(aline_user)
            db.commit()
            print("Aline user (Tesoureiro) created successfully!")
        else:
            # Keep role and admin status verified
            aline_user.role = "tesoureiro"
            aline_user.is_admin = True
            db.commit()

        # Ensure 'Membro' user exists as membro
        membro_user = db.query(User).filter(User.username == "membro").first()
        if not membro_user:
            print("Creating default Membro user...")
            hashed_membro = hash_password("membro123")
            membro_user = User(
                username="membro",
                email="membro@olorokebirigui.org",
                hashed_password=hashed_membro,
                is_active=True,
                is_admin=True,
                role="membro"
            )
            db.add(membro_user)
            db.commit()
            print("Membro user created successfully!")
        else:
            # Keep role and admin status verified
            membro_user.role = "membro"
            membro_user.is_admin = True
            db.commit()

        # 2. Seed avisos if empty
        if db.query(Aviso).count() == 0:
            print("Seeding initial avisos...")
            from app.routes import DEFAULT_AVISOS
            for item in DEFAULT_AVISOS:
                aviso = Aviso(
                    title=item["title"],
                    content=item["content"],
                    date_posted=item["date_posted"],
                    is_active=True
                )
                db.add(aviso)
            db.commit()

        # 3. Seed agenda events if empty
        if db.query(AgendaEvent).count() == 0:
            print("Seeding initial agenda events...")
            from app.routes import DEFAULT_EVENTS
            for item in DEFAULT_EVENTS:
                event = AgendaEvent(
                    title=item["title"],
                    description=item["description"],
                    date=item["date"],
                    time=item["time"],
                    type=item["type"],
                    status=item["status"]
                )
                db.add(event)
            db.commit()
            
        # 4. Seed internal announcements (Quadro de Avisos) if empty
        if db.query(QuadroAviso).count() == 0:
            print("Seeding initial internal announcement...")
            welcome_internal = QuadroAviso(
                title="Bem-vindo ao Quadro de Avisos Interno!",
                content="Este espaço é de uso restrito dos membros e administração da nossa Casa. Aqui publicamos informações sobre escalas, reuniões administrativas, manutenções do terreiro e comunicados de interesse exclusivo da nossa corrente. Mantenham-se atentos!",
                author_name="programador",
                date_posted=datetime.date.today(),
                created_at=datetime.datetime.utcnow()
            )
            db.add(welcome_internal)
            db.commit()
            print("Internal announcement seeded successfully!")

        # 5. Seed system configuration for house percentage if not exists
        porcentagem = db.query(ConfiguracaoSistema).filter(ConfiguracaoSistema.chave == "porcentagem_casa").first()
        if not porcentagem:
            print("Seeding default house percentage configuration...")
            porcentagem = ConfiguracaoSistema(
                chave="porcentagem_casa",
                valor="30.0"
            )
            db.add(porcentagem)
            db.commit()
            print("Default house percentage (30.0%) seeded successfully!")
            
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

# Attempt to automatically create database tables on startup
@app.on_event("startup")
def on_startup():
    try:
        print("Connecting to Supabase and creating database tables if they do not exist...")
        Base.metadata.create_all(bind=engine)
        print("Database tables synchronized successfully!")
        
        # Run custom schema migrations
        from app.models import migrate_membro_schema
        migrate_membro_schema(engine)

        from sqlalchemy import text
        with engine.begin() as conn:
            try:
                conn.execute(text("SELECT isento FROM mensalidades_pagamentos LIMIT 1"))
            except Exception:
                try:
                    conn.execute(text("ALTER TABLE mensalidades_pagamentos ADD COLUMN isento BOOLEAN DEFAULT FALSE"))
                    print("Added column 'isento' to 'mensalidades_pagamentos' successfully via migration!")
                except Exception as alter_err:
                    print(f"Could not add column isento: {alter_err}")

        seed_initial_data()
    except Exception as e:
        print(f"Warning: Could not create tables on remote database. Running in fallback mode. Details: {e}")

# If run directly (optional helper, usually uvicorn runs the module)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)

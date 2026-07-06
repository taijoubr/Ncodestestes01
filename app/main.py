from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from app.database import engine, Base
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
    same_site="none",
    https_only=True,
)

# Mount static files (images, css, icons)
# Ensure the static directory exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(BASE_DIR, "static/css"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static/images"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static/icons"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static/fonts"), exist_ok=True)

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
                content="Este espaço é de uso restrito do corpo mediúnico e administrativo da nossa Casa. Aqui publicamos informações sobre escalas, reuniões administrativas, manutenções do terreiro e comunicados de interesse exclusivo da nossa corrente. Mantenham-se atentos!",
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
        seed_initial_data()
    except Exception as e:
        print(f"Warning: Could not create tables on remote database. Running in fallback mode. Details: {e}")

# If run directly (optional helper, usually uvicorn runs the module)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)

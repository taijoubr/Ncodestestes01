import os
import json

db_firestore = None

def get_firestore_client():
    global db_firestore
    if db_firestore is not None:
        return db_firestore

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        project_id = os.getenv("FIREBASE_PROJECT_ID", "gen-lang-client-0498056765")
        database_id = os.getenv("FIREBASE_FIRESTORE_DATABASE_ID", "ai-studio-tendadeumbandaca-fa94416f-bc3a-455e-8b42-7dd973f8fda4")

        if not firebase_admin._apps:
            # Look for firebase-applet-config.json or environment variables
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase-applet-config.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r") as f:
                        cfg = json.load(f)
                        project_id = cfg.get("projectId", project_id)
                        database_id = cfg.get("firestoreDatabaseId", database_id)
                except Exception as ex:
                    print(f"Error reading firebase config file: {ex}")

            app = firebase_admin.initialize_app(options={"projectId": project_id})
            db_firestore = firestore.client(database=database_id)
            print(f"Firebase initialized successfully: Project={project_id}, Database={database_id}")
            return db_firestore
        else:
            app = firebase_admin.get_app()
            db_firestore = firestore.client(database=database_id)
            return db_firestore

    except Exception as e:
        print(f"Firebase client initialization note: {e}")
        return None

import os
import json
from google.cloud import firestore
import google.auth

# Cache client instance
_fs_client = None

def get_fs_client():
    """
    Returns an initialized Firestore client.
    Resolves the database ID and project ID from environment variables or config.json.
    """
    global _fs_client
    if _fs_client is not None:
        return _fs_client

    project_id = os.getenv("PROJECT_ID")
    if not project_id:
        try:
            _, project_id = google.auth.default()
        except Exception:
            project_id = "YOUR_DEFAULT_PROJECT_ID"

    # Load firestore database ID from configuration if available
    db_id = "(default)"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'data', 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                db_id = cfg.get("firestore_database", "(default)")
        except Exception as e:
            print(f"Warning: Failed to parse firestore_database from config: {e}")

    try:
        _fs_client = firestore.Client(project=project_id, database=db_id)
        return _fs_client
    except Exception as e:
        print(f"Error initializing Firestore Client: {e}")
        # Return fallback client with default settings
        _fs_client = firestore.Client(project=project_id)
        return _fs_client

def save_session_state(session_id: str, key: str, value: dict, collection: str = "agent_states"):
    """
    Persists target session state in Firestore, isolated by session_id.
    """
    client = get_fs_client()
    try:
        doc_ref = client.collection(collection).document(session_id)
        doc_ref.set({key: value}, merge=True)
    except Exception as e:
        print(f"Firestore save_session_state failed for key '{key}': {e}")
        raise e

def get_session_state(session_id: str, key: str, collection: str = "agent_states") -> dict:
    """
    Retrieves target session state from Firestore for a given session_id.
    """
    client = get_fs_client()
    try:
        doc_ref = client.collection(collection).document(session_id)
        doc = doc_ref.get()
        if doc.exists:
            d = doc.to_dict()
            return d.get(key, {})
        return {}
    except Exception as e:
        print(f"Firestore get_session_state failed for key '{key}': {e}")
        return {}

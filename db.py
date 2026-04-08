import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

firebase_config = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
}

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

users_collection = db.collection("users")

def add_user(user_id: int, full_name: str, birthdate: str, language: str = "en"):
    created_at = datetime.now().isoformat()
    users_collection.document(str(user_id)).set({
        "user_id": user_id,
        "full_name": full_name,
        "birthdate": birthdate,
        "language": language,
        "created_at": created_at,
        "is_approved": False,
        "role": "support",
    })

def approve_user(user_id: int):
    users_collection.document(str(user_id)).update({"is_approved": True})

def get_pending_users():
    docs = users_collection.where(filter=FieldFilter("is_approved", "==", False)).stream()
    return [doc.to_dict() for doc in docs]

def get_user(user_id: int):
    doc = users_collection.document(str(user_id)).get()
    if doc.exists:
        return doc.to_dict()
    return None

def update_language(user_id: int, language: str):
    users_collection.document(str(user_id)).update({
        "language": language
    })

def update_full_name(user_id: int, full_name: str):
    users_collection.document(str(user_id)).update({
        "full_name": full_name
    })

def update_birthdate(user_id: int, birthdate: str):
    users_collection.document(str(user_id)).update({
        "birthdate": birthdate
    })

def all_users():
    docs = users_collection.stream()
    return [doc.to_dict() for doc in docs]

def delete_user(user_id: int):
    users_collection.document(str(user_id)).delete()

def get_all_approved_users():
    docs = users_collection.where(filter=FieldFilter("is_approved", "==", True)).stream()
    return [doc.to_dict() for doc in docs]

def update_onboarding_stage(user_id: int, stage: int):
    users_collection.document(str(user_id)).update({"onboarding_stage": stage})

def set_role(user_id: int, role: str):
    users_collection.document(str(user_id)).update({"role": role})

def approve_user_with_role(user_id: int, role: str):
    users_collection.document(str(user_id)).update({"is_approved": True, "role": role})

def get_users_by_role(role: str):
    docs = (users_collection
            .where(filter=FieldFilter("is_approved", "==", True))
            .where(filter=FieldFilter("role", "==", role))
            .stream())
    return [doc.to_dict() for doc in docs]
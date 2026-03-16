import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore import AsyncClient

# Initialise Firebase Admin SDK once
# On Cloud Run: uses attached service account automatically
# Locally: uses GOOGLE_APPLICATION_CREDENTIALS env var
if not firebase_admin._apps:
    firebase_admin.initialize_app()

# Async Firestore client for non-blocking DB operations
db: AsyncClient = firestore.AsyncClient()

# Firebase Auth client
firebase_auth = auth
from google.cloud import firestore
from google.oauth2 import service_account  # <-- Agrega esta línea
from typing import List, Dict
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class DocumentStore:
    def __init__(self, chunk_size: int = 1000):
        # Cargar credenciales desde el archivo JSON
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        )
        self.db = firestore.Client(credentials=credentials)
        self.collection = self.db.collection("documents")
        self.chunk_size = chunk_size
        self.file_hashes: Dict[str, str] = {}

        # Cargar hashes existentes
        doc_ref = self.collection.document("metadata")
        doc = doc_ref.get()
        if doc.exists:
            self.file_hashes = doc.to_dict().get("file_hashes", {})

    def add_document(self, chunks: List[str]):
        batch = self.db.batch()
        for chunk in chunks:
            doc_ref = self.collection.document()
            batch.set(doc_ref, {"content": chunk, "tokens": len(chunk.encode('utf-8')) // 4})
        batch.commit()

    def get_all_chunks(self) -> List[str]:
        """Obtiene todos los chunks almacenados en Firestore."""
        return [doc.get("content") for doc in self.collection.stream()]

    def save_hashes(self):
        self.collection.document("metadata").set({"file_hashes": self.file_hashes})

    @classmethod
    def load(cls):
        return cls()
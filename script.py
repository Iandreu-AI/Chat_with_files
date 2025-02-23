import os
import pickle
import pdfplumber
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from docx import Document
from openai import OpenAI
from typing import Dict, Callable, List
from hashlib import md5

# Configuración
CONFIG = {
    "api_key": "sk-2bbfe7905cae4721a1f3f97af3fbf529",
    "base_url": "https://api.deepseek.com/v1/",
    "model": "deepseek-chat",
    "max_tokens": 4000,
    "context_window": 6000,
    "chunk_size": 1000,
    "persistence_file": "document_store.pkl"
}

client = OpenAI(api_key=CONFIG["api_key"], base_url=CONFIG["base_url"])

# Procesadores de archivos
FILE_PROCESSORS: Dict[str, Callable[[str], str]] = {
    '.pdf': lambda path: '\n'.join(p.extract_text() for p in pdfplumber.open(path).pages),
    '.docx': lambda path: '\n'.join(p.text for p in Document(path).paragraphs),
    '.txt': lambda path: Path(path).read_text(encoding='utf-8')
}


class DocumentStore:
    """Almacenamiento persistente de chunks de texto"""

    def __init__(self):
        self.chunks: List[str] = []
        self.file_hashes: Dict[str, str] = {}

    def add_document(self, chunks: List[str]):
        self.chunks.extend(chunks)

    def save(self):
        with open(CONFIG["persistence_file"], "wb") as f:
            pickle.dump((self.chunks, self.file_hashes), f)

    @classmethod
    def load(cls):
        try:
            with open(CONFIG["persistence_file"], "rb") as f:
                chunks, hashes = pickle.load(f)
            store = cls()
            store.chunks = chunks
            store.file_hashes = hashes
            return store
        except FileNotFoundError:
            return cls()


def token_count(text: str) -> int:
    return (len(text.encode('utf-8')) + 3) // 4


def chunk_text(text: str) -> List[str]:
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks, current_chunk, current_size = [], [], 0

    for para in paragraphs:
        para_size = token_count(para)
        if current_size + para_size > CONFIG["chunk_size"] and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk, current_size = [], 0
        current_chunk.append(para)
        current_size += para_size

    return chunks + ['\n'.join(current_chunk)] if current_chunk else chunks


def process_file(file_path: Path, store: DocumentStore) -> None:
    file_hash = md5(file_path.read_bytes()).hexdigest()

    if file_path.name in store.file_hashes and store.file_hashes[file_path.name] == file_hash:
        return

    processor = FILE_PROCESSORS.get(file_path.suffix.lower())
    if not processor:
        return

    text = processor(str(file_path))
    store.add_document(chunk_text(text))
    store.file_hashes[file_path.name] = file_hash


def find_relevant_chunks(question: str, store: DocumentStore) -> List[str]:
    """Busca chunks que contengan palabras clave de la pregunta."""
    keywords = set(question.lower().split())
    relevant_chunks = []

    for chunk in store.chunks:
        chunk_words = set(chunk.lower().split())
        if keywords & chunk_words:  # Intersección de palabras clave
            relevant_chunks.append(chunk)

    return relevant_chunks


def build_context(question: str, store: DocumentStore) -> str:
    relevant_chunks = find_relevant_chunks(question, store)
    context = []
    remaining_tokens = CONFIG["context_window"] - token_count(question) - 200

    for chunk in relevant_chunks:
        chunk_tokens = token_count(chunk)
        if chunk_tokens <= remaining_tokens:
            context.append(chunk)
            remaining_tokens -= chunk_tokens
        else:
            break

    return "Documentos:\n{}\n\nPregunta: {}".format('\n\n'.join(context), question)


def main():
    store = DocumentStore.load()

    root = tk.Tk()
    root.withdraw()

    if folder := filedialog.askdirectory(title="Seleccionar carpeta"):
        for file_path in Path(folder).rglob('*'):
            if file_path.suffix.lower() in FILE_PROCESSORS:
                process_file(file_path, store)
        store.save()
        print("Procesados {} chunks".format(len(store.chunks)))  # Error corregido aquí

    while (question := input("\nPregunta: ").strip().lower()) != "salir":
        if not question:
            continue

        try:
            context = build_context(question, store)
            response = client.chat.completions.create(
                model=CONFIG["model"],
                messages=[{
                    "role": "system",
                    "content": "Responde solo usando los documentos proporcionados o temas de los que se hablen en los documentos. Si el tema que te pregunta el usuario no esta directamente proporcionado en los documentos necesito que llegues a una respuesta basandote solo en lo que te han proporcionado los documentos'."
                }, {
                    "role": "user",
                    "content": context
                }],
                temperature=0.3
            )
            print("\nRespuesta:", response.choices[0].message.content)
        except Exception as e:
            print("Error: {}".format(str(e)))


if __name__ == "__main__":
    main()

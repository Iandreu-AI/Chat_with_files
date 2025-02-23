from pathlib import Path
from typing import List, Dict, Callable
import pdfplumber
from docx import Document
from core.config import Config
from core.document_store import DocumentStore

# Procesadores de archivos
FILE_PROCESSORS: Dict[str, Callable[[str], str]] = {
    '.pdf': lambda path: '\n'.join(p.extract_text() for p in pdfplumber.open(path).pages),
    '.docx': lambda path: '\n'.join(p.text for p in Document(path).paragraphs),
    '.txt': lambda path: Path(path).read_text(encoding='utf-8')
}


def token_count(text: str) -> int:
    """Calcula el número de tokens en un texto."""
    return (len(text.encode('utf-8')) + 3) // 4


def chunk_text(text: str, chunk_size: int) -> List[str]:
    """Divide el texto en chunks basados en un límite de tokens."""
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks, current_chunk, current_size = [], [], 0

    for para in paragraphs:
        para_size = token_count(para)
        if current_size + para_size > chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk, current_size = [], 0
        current_chunk.append(para)
        current_size += para_size

    return chunks + ['\n'.join(current_chunk)] if current_chunk else chunks


def process_file(file_path: Path, document_store: DocumentStore) -> None:
    """Procesa un archivo y agrega sus chunks al DocumentStore."""
    processor = FILE_PROCESSORS.get(file_path.suffix.lower())
    if not processor:
        return

    text = processor(str(file_path))
    chunks = chunk_text(text, document_store.chunk_size)
    document_store.add_document(chunks)


def build_context(question: str, document_store: DocumentStore) -> str:
    """Construye el contexto para una pregunta basado en los chunks almacenados."""
    relevant_chunks = document_store.get_all_chunks()
    context = []
    remaining_tokens = Config.CONTEXT_WINDOW - token_count(question) - 200  # Margen para la respuesta

    for chunk in relevant_chunks:
        chunk_tokens = token_count(chunk)
        if chunk_tokens <= remaining_tokens:
            context.append(chunk)
            remaining_tokens -= chunk_tokens
        else:
            break

    nl = "\n"  # Variable para el salto de línea
    return f"Documentos:{nl}{nl.join(context)}{nl}{nl}Pregunta: {question}"
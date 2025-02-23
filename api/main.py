from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import tempfile
from pathlib import Path
import os
from core.document_store import DocumentStore
from core.processors import process_file, build_context
from openai import OpenAI
from core.config import Config

# Configuración de la API
app = FastAPI()

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=Config.DEEPSEEK_API_KEY, base_url=Config.DEEPSEEK_BASE_URL)

# Inicializar el almacenamiento de documentos
document_store = DocumentStore(chunk_size=Config.CHUNK_SIZE)


# Ruta raíz
@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API de Chat con Archivos!"}


# Endpoint para subir archivos
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        for file in files:
            # Guardar el archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = Path(temp_file.name)

            # Procesar el archivo
            process_file(temp_path, document_store)
            os.unlink(temp_path)  # Eliminar el archivo temporal

        document_store.save_hashes()
        return {"message": f"{len(files)} archivos procesados exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para hacer preguntas
@app.post("/ask-question")
async def ask_question(question: str):
    try:
        # Construir el contexto basado en los documentos
        context = build_context(question, document_store)

        # Usar la API de Deepseek para generar una respuesta
        response = client.chat.completions.create(
            model=Config.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "Responde usando los documentos proporcionados."},
                {"role": "user", "content": context}
            ],
            temperature=0.3
        )
        return {"answer": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
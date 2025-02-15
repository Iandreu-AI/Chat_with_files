import os
import pdfplumber
from docx import Document
from openai import OpenAI

# Configuración de la API de DeepSeek
API_KEY = "sk-2bbfe7905cae4721a1f3f97af3fbf529"
BASE_URL = "https://api.deepseek.com/v1/"
MODEL_NAME = "deepseek-chat"
MAX_TOKENS = 4000
CONTEXT_WINDOW = 6000

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def procesar_archivos(ruta_carpeta: str) -> str:
    """Procesa archivos PDF, DOCX y TXT en una carpeta y consolida su texto."""
    texto_consolidado = ""
    extensiones_permitidas = {'.pdf', '.docx', '.txt'}

    for root_dir, _, files in os.walk(ruta_carpeta):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensiones_permitidas:
                ruta_archivo = os.path.join(root_dir, file)
                print(f"📄 Procesando {ruta_archivo}")
                if ext == ".pdf":
                    texto_consolidado += extraer_texto_pdf(ruta_archivo) + "\n"
                elif ext == ".docx":
                    texto_consolidado += extraer_texto_docx(ruta_archivo) + "\n"
                elif ext == ".txt":
                    texto_consolidado += extraer_texto_txt(ruta_archivo) + "\n"

    return texto_consolidado

def extraer_texto_pdf(ruta_pdf: str) -> str:
    """Extrae el texto de un archivo PDF."""
    texto = ""
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for pagina in pdf.pages:
                pagina_texto = pagina.extract_text()
                if pagina_texto:
                    texto += pagina_texto + "\n"
    except Exception as e:
        print(f"❌ Error al leer {ruta_pdf}: {e}")
    return texto

def extraer_texto_docx(ruta_docx: str) -> str:
    """Extrae el texto de un archivo DOCX."""
    texto = ""
    try:
        doc = Document(ruta_docx)
        for parrafo in doc.paragraphs:
            texto += parrafo.text + "\n"
    except Exception as e:
        print(f"❌ Error al leer {ruta_docx}: {e}")
    return texto

def extraer_texto_txt(ruta_txt: str) -> str:
    """Extrae el texto de un archivo TXT."""
    texto = ""
    try:
        with open(ruta_txt, "r", encoding="utf-8") as file:
            texto = file.read()
    except Exception as e:
        print(f"❌ Error al leer {ruta_txt}: {e}")
    return texto

def responder_preguntas(pregunta: str) -> str:
    """Realiza preguntas sobre los documentos analizados y devuelve la respuesta."""
    try:
        texto_consolidado = "Tu texto consolidado aquí"
        contexto = f"Document Context:\n{texto_consolidado}\n\nQuestion: {pregunta}"
        respuesta = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Responde solo con base en el contexto proporcionado."},
                {"role": "user", "content": contexto}
            ],
            temperature=0.3,
            max_tokens=MAX_TOKENS
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error al procesar la respuesta: {e}")

import os
from flask import Flask, request, jsonify
from script import procesar_archivos

app = Flask(__name__)

@app.route("/procesar", methods=["POST"])
def procesar_endpoint():
    """Esperar JSON con {'ruta_carpeta': '...'} para procesar la carpeta."""
    data = request.json
    if not data or "ruta_carpeta" not in data:
        return jsonify({"error": "Se requiere 'ruta_carpeta' en el body"}), 400

    ruta = data["ruta_carpeta"]
    try:
        resultado = procesar_archivos(ruta)
        return jsonify({"resultado": resultado})
    except Exception as e:
        return jsonify({"error": f"Error al procesar la carpeta: {str(e)}"}), 500

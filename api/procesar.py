from flask import Flask, request, jsonify
from programa import procesar_carpeta, responder_pregunta

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"mensaje": "Bienvenido a la API de Procesamiento de Archivos"})

@app.route("/procesar", methods=["POST"])
def procesar_endpoint():
    """
    Espera un JSON con {"ruta_carpeta": "..."} para procesar la carpeta.
    """
    data = request.json
    if not data or "ruta_carpeta" not in data:
        return jsonify({"error": "Se requiere 'ruta_carpeta' en el body"}), 400

    ruta = data["ruta_carpeta"]
    resultado = procesar_carpeta(ruta)
    return jsonify({"resultado": resultado})

@app.route("/preguntar", methods=["POST"])
def preguntar_endpoint():
    """
    Espera un JSON con {"pregunta": "..."} para obtener respuesta.
    """
    data = request.json
    if not data or "pregunta" not in data:
        return jsonify({"error": "Se requiere 'pregunta' en el body"}), 400

    pregunta = data["pregunta"]
    respuesta = responder_pregunta(pregunta)
    return jsonify({"respuesta": respuesta})

# Esta línea es solo para Vercel, no uses `app.run()`.
if __name__ == "__main__":
    app.run(debug=True, port=5000)

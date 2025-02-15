from flask import Flask, request, jsonify
from script import responder_preguntas

app = Flask(__name__)

@app.route("/preguntar", methods=["POST"])
def preguntar_endpoint():
    """Esperar JSON con {'pregunta': '...'} para obtener respuesta."""
    data = request.json
    if not data or "pregunta" not in data:
        return jsonify({"error": "Se requiere 'pregunta' en el body"}), 400

    pregunta = data["pregunta"]
    try:
        respuesta = responder_preguntas(pregunta)
        return jsonify({"respuesta": respuesta})
    except Exception as e:
        return jsonify({"error": f"Error al responder la pregunta: {str(e)}"}), 500

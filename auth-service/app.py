from flask import Flask, request, jsonify
import json
import time

app = Flask(__name__)

# Cargar API keys de la base de datos simulada
with open("data/api_keys.json", "r") as file:
    api_keys = json.load(file)

rate_limits = {}
users_last_request = {}

@app.route("/validate", methods=["POST"])
def validate_key():
    data = request.get_json()
    api_key = data.get("api_key")

    if not api_key:
        return jsonify({"error": "Missing API Key"}), 400

    user_config = api_keys.get(api_key)

    if not user_config:
        return jsonify({"valid": False}), 403

    max_rpm = user_config["max_rpm"]
    current_time = time.time()
    last_request_time = users_last_request.get(api_key, 0)

    # Inicializar el contador de solicitudes si no existe
    if api_key not in rate_limits:
        rate_limits[api_key] = 0

    # Reiniciar contador si ha pasado la ventana de 60 segundos
    if current_time - last_request_time >= 60:
        rate_limits[api_key] = 0
        users_last_request[api_key] = current_time

    # Verificar si se ha alcanzado el límite
    if rate_limits[api_key] >= max_rpm:
        return jsonify({"error": "Rate limit exceeded"}), 429

    # Incrementar el contador y actualizar el tiempo de la última solicitud
    rate_limits[api_key] += 1
    users_last_request[api_key] = current_time

    return jsonify({"valid": True, "type": user_config["type"], "max_rpm": max_rpm}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

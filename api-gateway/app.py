from flask import Flask, request, jsonify
import requests
import os
import yaml
import time
import pytz
from datetime import datetime

app = Flask(__name__)

# Cargar configuración desde config/config.yaml
config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
with open(config_path, "r") as config_file:
    config = yaml.safe_load(config_file)

# Acceso a las configuraciones
cache_service_url = config["cache_service_url"]
model_service_url = config["model_service_url"]
log_service_url = config["log_service_url"]
auth_service_url = config["auth_service_url"]
local_tz = pytz.timezone(config["timezone"])

def get_current_time():
    """Obtener la hora actual en formato local."""
    return datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")

@app.route("/service", methods=["POST"])
def service():
    api_key = request.headers.get("Authorization")
    if not api_key:
        return jsonify({"error": "Unauthorized: Missing API Key"}), 401

    # Llamar al auth-service para validar la API Key y rate limit
    auth_response = requests.post(auth_service_url, json={"api_key": api_key})
    if auth_response.status_code != 200:
        return jsonify({"error": "Unauthorized: Invalid API Key"}), auth_response.status_code

    auth_data = auth_response.json()
    if not auth_data.get("valid"):
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 403

    # Validar rate limit
    if "rate_limit_exceeded" in auth_data and auth_data["rate_limit_exceeded"]:
        return jsonify({"error": "Rate limit exceeded"}), 429

    request_data = request.json
    if not request_data:
        return jsonify({"error": "Invalid input: 'inputs' field is required"}), 400
    cache_key = f"{api_key}:{str(request_data)}"  # Generar un key único para el request

    # Buscar en cache
    cache_response = requests.get(cache_service_url, params={"key": cache_key})
    if cache_response.status_code == 200:
        cached_data = cache_response.json().get("value", {})
        return jsonify(cached_data), 200

    # Si no está en cache, llamar al model-service y guardar en cache
    try:
      model_response = requests.post(model_service_url, json=request_data)
      if model_response.status_code == 200:
        model_data = model_response.json()
        cache_data = {
            "key": cache_key,
            "value": model_data
        }
        requests.post(cache_service_url, json=cache_data)
        return jsonify(model_data), 200
      # Manejar errores del model-service
      else:
        return jsonify({"error": "Model service error", "details": model_response.json()}), model_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Model service connection error", "details": str(e)}), 503
    # return jsonify(model_response.json()), model_response.status_code

def log_to_service(log_entry):
    """Enviar log al servicio de logging."""
    try:
        requests.post(log_service_url, json={"log_entry": log_entry})
    except Exception as e:
        print(f"Error enviando log: {e}")

@app.before_request
def log_request():
    log_entry = {
        "timestamp": get_current_time(),
        "service": "api-gateway",
        "event": "request",
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "body": request.get_json(silent=True)
    }
    log_to_service(log_entry)

@app.after_request
def log_response(response):
    log_entry = {
        "timestamp": get_current_time(),
        "service": "api-gateway",
        "event": "response",
        "status_code": response.status_code,
        "response_headers": dict(response.headers),
        "response_body": response.get_json(silent=True)
    }
    log_to_service(log_entry)
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

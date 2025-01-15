from flask import Flask, request, jsonify
import requests
import yaml
import time
import pytz
from datetime import datetime

app = Flask(__name__)

with open("config/rate_limit_config.yaml", "r") as file:
    rate_limit_config = yaml.safe_load(file)

rate_limits = {}
users_last_request = {}

cache_service_url = "http://cache-service:5003/cache"
model_service_url = "http://model-service:5002/get_related_entities"
LOG_SERVICE_URL = "http://log-service:5008/log"

local_tz = pytz.timezone("America/Argentina/Buenos_Aires")

def get_current_time():
    return datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")

@app.route("/service", methods=["POST"])
def service():
  api_key = request.headers.get("Authorization")
    
  if not api_key:
    return jsonify({ "error": "Unauthorized: Missing API Key"}), 401

  user_config = rate_limit_config["API_KEYS"].get(api_key)

  if not user_config:
    return jsonify({"error": "Unauthorized: Invalid API Key"}), 403

  max_rpm = user_config["max_rpm"]
  current_time = time.time()
  last_request_time = users_last_request.get(api_key, 0)

  if api_key in rate_limits and rate_limits[api_key] >= max_rpm:
    if current_time - last_request_time < 60:
      return jsonify({"error": "Rate limit exceeded"}), 429

  request_data = request.json
  cache_key = f"{api_key}:{str(request_data)}"  # Generar un key único para el request
    
  # Buscar en cache
  cache_response = requests.get(cache_service_url, params={"key": cache_key})

  # Esta en la cache entonces sacamos de la cache
  if cache_response.status_code == 200:
    cached_data = cache_response.json().get("value", {})
    return jsonify(cached_data), 200

  # Si no está en cache, llamar al model-service y guardamos en cache
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
  return jsonify(requests.post(model_service_url, json=request.json).json()), requests.post(model_service_url, json=request.json).status_code


def log_to_service(log_entry):
    """Enviar log al servicio de logging"""
    try:
        requests.post(LOG_SERVICE_URL, json={"log_entry": log_entry})
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

from flask import Flask, request, jsonify
import requests
import yaml
import time
import urllib.parse

app = Flask(__name__)

with open("config/rate_limit_config.yaml", "r") as file:
    rate_limit_config = yaml.safe_load(file)

rate_limits = {}
users_last_request = {}

cache_service_url = "http://cache-service:5003/cache"
model_service_url = "http://model-service:5002/get_related_entities"

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
  return jsonify({"error": "Error en model-service", "details": model_response.json()}), model_response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

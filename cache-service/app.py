import time
from flask import Flask, request, jsonify
import redis
import json 
import logging
import pytz
from datetime import datetime

app = Flask(__name__)

# Cache simulado como un diccionario en memoria
# cache = {}
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)


@app.route('/cache', methods=['GET', 'POST'])
def manage_cache():
  
  if request.method == "GET":
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "Key is required"}), 400
    value = redis_client.get(key)
    if value:
      try:
        # Intenta deserializar si el valor está en formato JSON
        value = json.loads(value)
      except json.JSONDecodeError:
        pass  # Si no es JSON, pasa el valor directamente
      return jsonify({"key": key, "value": value}), 200
    else:
      app.logger.info("Entramos aqui en 404.....", flush=True)
      return jsonify({"error": "Key not found"}), 404

  if request.method == "POST":
    data = request.json
    key = data.get("key")
    value = data.get("value")
    ttl = data.get("ttl", 1800)  # TTL en segundos (por defecto, 60 segundos)
    if not key or value is None:
      return jsonify({"error": "Key and value are required"}), 400
    if not isinstance(value, dict) or "entity_id" not in value or "top10_entities" not in value or "top10_scores" not in value:
      return jsonify({"error": "Invalid value format"}), 400
    try:
      # Serializa el valor a JSON antes de guardarlo
      redis_client.set(key, json.dumps(value), ex=ttl)
    except Exception as e:
      return jsonify({"error": "Failed to set value in cache", "details": str(e)}), 500
    return jsonify({"key": key, "value": value, "ttl": ttl}), 201
  
  LOG_SERVICE_URL = "http://log-service:5008/log"
local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
def get_current_time():
    return datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")

def log_to_service(log_entry):
    try:
        requests.post(LOG_SERVICE_URL, json={"log_entry": log_entry})
    except Exception as e:
        print(f"Error enviando log: {e}")

@app.before_request
def log_request():
    log_entry = {
        "timestamp": get_current_time(),
        "service": "cache-service",
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
        "service": "cache-service",
        "event": "response",
        "status_code": response.status_code,
        "response_headers": dict(response.headers),
        "response_body": response.get_json(silent=True)
    }
    log_to_service(log_entry)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

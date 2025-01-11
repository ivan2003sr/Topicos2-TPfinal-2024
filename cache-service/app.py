from flask import Flask, request, jsonify
import redis
import json 
import logging


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

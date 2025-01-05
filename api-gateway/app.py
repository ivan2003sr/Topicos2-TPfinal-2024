from flask import Flask, request, jsonify
import requests
import yaml
import time

app = Flask(__name__)

with open("config/rate_limit_config.yaml", "r") as file:
    rate_limit_config = yaml.safe_load(file)

rate_limits = {}
users_last_request = {}

@app.route("/service", methods=["POST"])
def service():
    api_key = request.headers.get("Authorization")
    
    if not api_key:
            return jsonify({
        "error": "Unauthorized: Missing API Key"
    }), 401

    user_config = rate_limit_config["API_KEYS"].get(api_key)

    if not user_config:
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 403


    max_rpm = user_config["max_rpm"]
    current_time = time.time()
    last_request_time = users_last_request.get(api_key, 0)

    if api_key in rate_limits and rate_limits[api_key] >= max_rpm:
        if current_time - last_request_time < 60:
            return jsonify({"error": "Rate limit exceeded"}), 429

    users_last_request[api_key] = current_time
    rate_limits[api_key] = rate_limits.get(api_key, 0) + 1

    model_service_url = "http://model-service:5002/process"
    response = requests.post(model_service_url, json=request.json)
    
    if response.status_code != 200:
        return jsonify({"error": "Error al procesar el modelo"}), response.status_code
    
    return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

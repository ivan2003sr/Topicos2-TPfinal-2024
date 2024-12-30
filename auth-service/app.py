from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Cargar API keys de la base de datos simulada
with open("data/api_keys.json", "r") as file:
    api_keys = json.load(file)

@app.route("/validate", methods=["POST"])
def validate_key():
    data = request.get_json()
    api_key = data.get("api_key")
    
    if not api_key:
        return jsonify({"error": "Missing API Key"}), 400

    if api_key in api_keys:
        return jsonify({"valid": True, "type": api_keys[api_key]["type"]}), 200
    else:
        return jsonify({"valid": False}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

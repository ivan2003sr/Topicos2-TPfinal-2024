from flask import Flask, jsonify, request

app = Flask(__name__)

# Cache simulado como un diccionario en memoria
cache = {}

@app.route('/cache', methods=['GET', 'POST'])
def manage_cache():
    if request.method == 'POST':
        # Agregar o actualizar en la caché
        data = request.json
        key = data.get("key")
        value = data.get("value")
        if key and value:
            cache[key] = value
            return jsonify({"message": "Value stored in cache"}), 200
        return jsonify({"error": "Key and value are required"}), 400
    elif request.method == 'GET':
        # Obtener un valor de la caché
        key = request.args.get("key")
        if key in cache:
            return jsonify({"value": cache[key]}), 200
        return jsonify({"error": "Key not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

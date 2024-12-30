from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_model():
    # Simulación de procesamiento de un modelo
    data = request.json
    inputs = data.get("inputs", [])
    
    # Respuesta genérica
    response = {
        "probabilidad": 0.7  # Valor fijo simulado
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

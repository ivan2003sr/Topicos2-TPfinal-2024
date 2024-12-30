from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def log_event():
    # Recibir datos de registro
    data = request.json
    log_entry = data.get("log_entry", "Default log entry")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar en el archivo de logs
    with open('./logs/service_logs.log', 'a') as f:
        f.write(f"{timestamp} - {log_entry}\n")

    return jsonify({"message": "Log saved"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)

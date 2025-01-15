import logging
import os
from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

log_directory = "./logs"
local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
current_time = datetime.now(local_tz)

log_filename = current_time.strftime("logs.%Y-%m-%d__%H_%M_%S.log")
log_file = os.path.join(log_directory, log_filename)

log_message = current_time.strftime("LOGS DE LA SESIÓN INICIADA EL %d/%m/%Y A LAS %H:%M:%S")
log_path = os.path.join(log_directory, log_filename)

os.makedirs(log_directory, exist_ok=True)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S%z')

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

for handler in logging.root.handlers:
    handler.setFormatter(log_formatter)

with open(log_path, "w") as log_file:
    log_file.write(log_message + "\n\n")

@app.route('/log', methods=['POST'])
def log_event():
    data = request.json
    log_entry = data.get("log_entry", "Default log entry")
    logging.info(f"{log_entry}")
    return jsonify({"message": "Log saved"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)

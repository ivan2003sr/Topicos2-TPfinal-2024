from flask import abort, jsonify,Flask, request
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import pandas as pd
import torch
import numpy as np

def create_app(test_config=None):
  app = Flask(__name__)
  # app.run(host='0.0.0.0', port=5002, debug=True)
  try:
    model = torch.load('model/trained_model.pkl', weights_only=False)
    print("Modelo cargado correctamente.")
  except Exception as e:
    print(f"Error al cargar el modelo: {e}")


  # -----------------Este es un ejemplo de Simulación de procesamiento de un modelo------------------
  @app.route('/process', methods=['POST'])
  def process_model():
    data = request.json
    inputs = data.get("inputs", [])    
    # Respuesta genérica
    response = {
        "probabilidad": 0.7  # Valor fijo simulado
    }
    return jsonify(response), 200


  return app

app = create_app()


from flask import Flask
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import pandas as pd
import torch
import numpy as np

def create_app():
    app = Flask(__name__)

    # Configuraciones de la app
    app.config.from_pyfile('config/model_config.yaml')
    model = torch.load('model/trained_model.pkl', weights_only=False)

    # Registrar rutas si es necesario
    @app.route("/")
    def home():
      return "¡Bienvenido a la API de detección de similitudes!"
    
    @app.route('/predict', methods=['POST','GET'])
    def predict():
      return "¡Bienvenido a la API de detección de similitudes!"
    
    return app

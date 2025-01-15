import time
from flask import abort, jsonify,Flask, request
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import pandas as pd
import torch
import numpy as np
import pytz
from datetime import datetime

def create_app(test_config=None):
  app = Flask(__name__)
  app.config['DEBUG'] = True

  try:
    # Cargamos el modelo
    model = torch.load('/app/app/model/trained_model.pkl', weights_only=False, map_location=torch.device('cpu'))
    print("Modelo cargado correctamente y dataset de entrenamiento.")

    # Cargamos el grafo de conocimiento que se entreno
    triples_file = '/app/app/dataset/dataset_train.tsv.gz'
    triples_factory = TriplesFactory.from_path(triples_file, create_inverse_triples=True)
    df = pd.read_csv(triples_file, sep='\t', header=None, names=['head', 'relation', 'tail'])
    print("Dataset de tripletas cargadas")


  except Exception as e:
    print(f"Error al cargar el modelo: {e}")







  # Endpoint para obtener las 10 mejores entidades relacionadas por un ID de entidad
  @app.route('/get_related_entities', methods=['POST'])
  def get_related_entities():

    #try:
      # Obtener datos del request
      data = request.json
      entity_id = data.get("entity_id")  # Obtener el ID de la entidad

      print(f"Entity ID recibido: {entity_id}")
      
      # if entity_id is None:
      #   print("Error: No se proporcionó entity_id")
      #   return jsonify({"error": "No entity_id provided"}), 400
      

      # if entity_id not in triples_factory.entity_to_id.values():
      #   print(f"Error: La entidad ID {entity_id} no encontrado en el grafo")
      #   return jsonify({"error": "Entity ID not found"}), 404
      heads = df[list(map(lambda x: True if ('pronto.owl#space_site' in x) and (len(x.split('#')[1].split('_')) == 3) else False, df['head'].values))]['head'].values
      heads_idx = [triples_factory.entity_to_id[head] for head in heads]
      
      # entity_idx = triples_factory.entity_to_id[entity_id]
      entity_idx = entity_id
      print(f"ID de la entidad: {entity_idx}")

      if entity_idx not in heads_idx:
        return jsonify({"error": f"Entity ID '{entity_id}' does not match any unique entity"}), 404
        
     
      relation_idx = triples_factory.relation_to_id['http://www.w3.org/2002/07/owl#sameAs']
      
      # Crear el tensor para la entidad proporcionada
      sample = torch.tensor([[entity_idx, relation_idx]])
      print(f"Procesando la entidad: {entity_id}")
      
      # Limpiar caché de CUDA (si aplica)
      torch.cuda.empty_cache()
      
      # Obtener los scores del modelo
      scores = model.score_t(sample)
      print(f"Scores generados por el modelo: {scores}")
      
      # Obtener los 10 mejores
      top_candidates = scores.topk(10, largest=False)
      print(f"Top Candidates: {top_candidates}")
      
      top_values = top_candidates.values.tolist()
      top_indices = top_candidates.indices.tolist()
      print(f"Top Scores: {top_values}")
      print(f"Top Indices: {top_indices}")
      
    
      # Respuesta exitosa
      response = {
          "entity_id": entity_idx,
          "top10_entities": top_indices,
          "top10_scores": top_values,
      }
      return jsonify(response), 200

    # except Exception as e:
    #   # Capturar cualquier error
    #   print(f"Error interno: {str(e)}")
    #   return jsonify({"error": f"Internal server error: {str(e)}"}), 500

  

  return app

app = create_app()

LOG_SERVICE_URL = "http://log-service:5008/log"
local_tz = pytz.timezone("America/Argentina/Buenos_Aires")

def get_current_time():
    return datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")

def log_to_service(log_entry):
    """Enviar log al servicio de logging"""
    try:
        requests.post(LOG_SERVICE_URL, json={"log_entry": log_entry})
    except Exception as e:
        print(f"Error enviando log: {e}")

@app.before_request
def log_request():
    log_entry = {
        "timestamp": get_current_time(),
        "service": "model-service",
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
        "service": "model-service",
        "event": "response",
        "status_code": response.status_code,
        "response_headers": dict(response.headers),
        "response_body": response.get_json(silent=True)
    }
    log_to_service(log_entry)
    return response
import os

from flask import (
    Flask,
    request,
    Response,
    abort,
    jsonify,
)  # se importa la librería principal de flask
import numpy as np
import tensorflow as tf
from flaskr.db import get_db
from datetime import datetime

from bson.json_util import dumps


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.route("/predict", methods=["GET", "POST"])
    def predict():
        sueldo_basico = request.args.get("sueldo_basico")
        categoria = request.args.get("categoria")
        ausencias = request.args.get("ausencias")
        cantidad_hijos = request.args.get("cantidad_hijos")
        error = None

        model = tf.keras.models.load_model("../../0_ML/model.keras")

        if not sueldo_basico:
            error = "sueldo_basico is required."
        elif not categoria:
            error = "categoria is required."
        elif not ausencias:
            error = "ausencias is required."
        elif not cantidad_hijos:
            error = "cantidad_hijos is required."

        if error:
            abort(404, description=error)

        param = np.array([sueldo_basico, ausencias, cantidad_hijos])
        match categoria:
            case "A":
                param = np.append(param, [1, 0, 0])

            case "B":
                param = np.append(param, [0, 1, 0])

            case "C":
                param = np.append(param, [0, 0, 1])
        param = np.array([[sueldo_basico, cantidad_hijos, 2, 1, 0, 0]]).astype(
            "float32"
        )

        result = model.predict(param)
        #
        # get_db() -> resuelve una conexión a la base de datos
        # request_log -> es una colección en la base de datos
        # insert_one() -> persiste el JSON que recibe como parámetro
        #
        get_db().request_log.insert_one( 
            {
                "timestamp": datetime.now().isoformat(), # formateo de la fecha
                "params": param[0].tolist(),  #capturamos los parámetros de la invocación
                "response": result[0].tolist(), #capturamos el resultado
            }
        )
        return jsonify(result.tolist())
        
    @app.route('/requests',methods=['GET', 'POST'])
    def requests():
        result=get_db().request_log.find()
        # se convierte el cursor a una lista
        list_cur = list(result)         
        # se serializan los objetos
        json_data = dumps(list_cur, indent = 2)  
        #retornamos la rista con los metadatos adecuados
        return Response(json_data,mimetype='application/json')

    return app

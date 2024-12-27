import os

from flask import abort, jsonify,Flask, request
import numpy as np

from datetime import datetime
from flaskr.db import get_db
import tensorflow as tf

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.run(host='0.0.0.0', port=80, debug=True)

    model=tf.keras.models.load_model('model.keras')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/predict', methods=['POST','GET'])
    def predict():

        sueldo_basico= (request.args.get('sueldo_basico'))
        categoria= request.args.get('categoria')
        ausencias= (request.args.get('ausencias'))
        cantidad_hijos= (request.args.get('cantidad_hijos'))

        error = None
        if not sueldo_basico:
            error = 'Sueldo basico no valido'
        elif not categoria:
            error = 'Categoria no valido'
        elif not ausencias:
            error = 'Ausencias no valido'
        elif not cantidad_hijos:
            error = 'cantidad_hijos no valido'
        if error:
            abort(400, description=error)

        array=[sueldo_basico,ausencias,cantidad_hijos]
        match categoria:
                case "A":
                    array+= [1,0,0]
                case "B":
                    array += [0, 1, 0]
                case "C":
                    array+= [0,0,1]

        param = np.array([array]).astype(np.float32)


        result = model.predict(param)

        #get_db().request_log.insert_one({
        #    "timestamp": datetime.now(),
        #    "params":param[0].tolist(),
        #    "result":result[0].tolist()
        #})
        return jsonify(result.tolist())

    return app
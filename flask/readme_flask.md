# Fuentes

Principalmente las de Flask

# crear el proyecto y configurar el env
Referencia: https://flask.palletsprojects.com/en/3.0.x/installation/
```
mkdir app
cd app
python3 -m venv .venv
```

Activar

``source .venv/bin/activate``

Instalar Flask

``pip install Flask numpy tensorflow``

# Empezamos a programar a app

Creamos la carpeta de código fuente

``mkdir flaskr``

Application factory:`flaskr/__init__.py`


```
import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
```



Corramos la app

`flask --app flaskr run --debug`

La probamos

`curl http://127.0.0.1:5000/hello`

# Endpoint predict

Definimos un endpoint para las opciones GET/POST

```

from flask import abort, jsonify,Flask, request

@app.route('/predict',methods=['GET', 'POST'])
    def predict():
    result=None
    return jsonify(result)

```

Instalamos algunas librerias necesarias dentro del proyecto
```
pip3 install tensorflow pandas
```

Suponiendo que el servicio va a ser invocado con la siguiente URL, extraemos los parámetros de la URL:

`http://127.0.0.1:5000/predict?sueldo_basico=34000&categoria=B&ausencias=0&cantidad_hijos=2&`

```
        sueldo_basico = request.args.get('sueldo_basico')
        categoria = request.args.get('categoria')
        ausencias = request.args.get('ausencias')
        cantidad_hijos = request.args.get('cantidad_hijos')
```

Agregamos la validación de que no sean vacios:

```
        error = None

        if not sueldo_basico:
            error = 'sueldo_basico is required.'
        elif not categoria:
            error = 'categoria is required.'
        elif not ausencias:
            error = 'ausencias is required.'
        elif not cantidad_hijos:
            error = 'cantidad_hijos is required.'

        if error:
            abort(404, description=error) 
```

Una vez que contaos con todos los parámetros, nos disponemos a producir un array Numpy para que pueda ser utilizado con la fonción `model.predict()``

```
        import numpy as np #Manejar los arreglos con los datos
        
        array=[sueldo_basico,ausencias,cantidad_hijos]
```

Dado que la categoria es un flag, tenemos que armar la cola del vector:
```
        match categoria:
                case "A":
                    array+= [1,0,0]
                case "B":
                    array += [0, 1, 0]
                case "C":
                    array+= [0,0,1]
```

Finalmente preparamos los parametros para predecir:
```
        param = np.array([array]).astype(np.float32)

```



Finalmente ajustamos el retorno:

```
return jsonify(param.tolist())

```

# Cargamos el modelo al inicializar la app

Una vez entrenado el modelo, podríamos utilizarlo en nuestro servicio. Para ello, vamos a leer el modelo desde un archivo y dejarlo disponible en una variable local.

```
   import tensorflow as tf

    model = tf.keras.models.load_model("../../0_ML/model.keras")
```

Luego vamos a ajustar la funcion `predict()` para utilizar el modelo y luego retornar el resultado.

```
        result=model.predict(param)
        return jsonify(result.tolist())

```


# Incorporamos una db

En primer lugar, debemos iniciar una base de datos. Existen dos opciones:

## Utilizar una instancia local de MongoDB

Se podría utilizar docker e iniciar un contenedor con el siguiente comando:

```
docker run -d --network some-network --name some-mongo \
	-e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
	-e MONGO_INITDB_ROOT_PASSWORD=secret \
	mongo`
```

## Utilzar una instancia en la nube

Una opción en la nube es https://cloud.mongodb.com/ que brinda un servicio de Mongo DB.
Los pasos para activar una cuenta son:

1. Registrar una cuenta
2. Obtener la URL de conexión accediendo a
    1. Elegir `Database` desde el panel izquierdo
    2. Presionar `Connect``
    3. Elegir `Driver` y capturar el string de conexión de la sección 3.
3. Ajustar las credenciales (usuario/clave).
    1. Elegir `Database Access` desde el panel isquierdo.
    2. Presionar `Edit` en el usuario existente
    3. Ajustemos el password.

## Integración en nuestra aplicación

Instalemos la librería de Mongo: `pip3 install pymongo`

Creemos el conectror en: `flaskr/db.py`. Por favor notar que se debe reemplazar


```
import pymongo

from flask import current_app, g

def get_db():
    if 'db' not in g:
        print("registramos una conexión")
        dbClient = pymongo.MongoClient("mongodb+srv://<user>:<pass>@cluster0.g2znx.gcp.mongodb.net/?retryWrites=true&w=majority") # Ajustar la linea de acuerdo al servidor utiizado
        dbName="mydatabase"
        db = dbClient[dbName]
        g.db=db
            

    return g.db


```

Posteriormente, registramos los parámetros y la salida del llamado al servicio en la base de datos Mongo.

```
        from datetime 


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
```

Por ultimo podemos exponer un servicio para conocer todas las invocaciones registradas en el sistema. Para ello vamos a exponer el siguiente endpoint:

`http://127.0.0.1:5000/requests`

El nuevo endpoint podría ser:
```
    @app.route('/requests',methods=['GET', 'POST'])
    def requests():
        result=get_db().request_log.find()
        # se convierte el cursor a una lista
        list_cur = list(result)         
        # se serializan los objetos
        json_data = dumps(list_cur, indent = 2)  
        #retornamos la rista con los metadatos adecuados
        return Response(json_data,mimetype='application/json')



```
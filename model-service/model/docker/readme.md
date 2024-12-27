# Docker compose

## Dependencias
Capturemos las dependencias del proyecto de Flask

```
pip freeze > requirements.txt
```
## Directorio de trabajo

Ir al directorio de trabajo donde se encuentra el código fuente.

## Definamos nuestra primer imagen


En una archivo DockerFile
```
FROM python:3.12
WORKDIR /usr/local/app/

# instalemos las dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copiemos el código fuente
COPY <reemplazar por la ruta del código fuente> ./src

# creemos un usuario
RUN useradd app
USER app

WORKDIR ./

CMD ["comando", "parametro1", "parametro2", "..."]

```

# Construyamos la imagen

```sudo docker build . -t servidorml```


Iniciemos el servidor

```
sudo docker run -p 5001:5000 --name srv  servidorml:latest
```

# Problema
## ¿Porqué no arranca?


Debemos revisar si la app es iniciada en el directorio correcto.

```
WORKDIR ./src/app
```

## ¿Funciona la app?

Flask inicia en modo desarrollo y no permite conexiones desde una IP que no fuese 127.0.0.1. Por lo tanto debemos indicar que se puedan establecer conexiones desde cualquier dirección:

```
CMD ["flask", "--app", "flaskr", "run","--debug","-h","0.0.0.0"]
```




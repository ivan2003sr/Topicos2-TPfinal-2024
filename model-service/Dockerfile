# Usa una imagen base de Python ligera
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/local/app/

# Copia los archivos de configuración
COPY requirements.txt ./

# Instalamos las dependencias del microservicio
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el codigo fuente al contenedor
COPY ./app ./app

# creemos un usuario
RUN useradd app
USER app

# Expone el puerto que usará el servicio (en este caso 5000)
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["flask", "--app", "app.main", "run","--debug","-h","0.0.0.0"]

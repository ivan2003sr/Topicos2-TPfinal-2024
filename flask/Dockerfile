FROM python:3.12
WORKDIR /usr/local/app/

# instalemos las dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copiemos el código fuente
COPY ./app ./src/app

# creemos un usuario
RUN useradd app
USER app
#EXPOSE 5000

WORKDIR  /src/app

CMD ["flask", "--app", "flaskr", "run","--debug","-h","0.0.0.0"]
#CMD ["ls"]
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5002
CMD ["flask", "--app", "app", "run", "--debug", "--host=0.0.0.0", "--port=5002"]

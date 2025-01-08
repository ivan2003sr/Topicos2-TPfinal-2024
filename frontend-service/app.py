from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

API_GATEWAY_URL = "http://api-gateway:5000/service"

@app.route("/")
def home():
    return redirect(url_for("service_form"))

@app.route("/service", methods=["GET", "POST"])
def service_form():
    if request.method == "POST":
        entity_id = request.form.get("entity_id")
        api_key = request.form.get("api_key")

        if not api_key:
            flash("Por favor, ingresa tu API Key.", "error")
            return redirect(url_for("service_form"))

        if not entity_id:
            flash("Por favor, ingresa un ID de entidad.", "error")
            return redirect(url_for("service_form"))

        payload = {"entity_id": entity_id}
        headers = {"Authorization": api_key, "Content-Type": "application/json"}

        try:
            response = requests.post(API_GATEWAY_URL, json=payload, headers=headers)
            response.raise_for_status()  
            data = response.json()
            return render_template("result.html", data=data)

        except requests.exceptions.HTTPError as http_err:
            # Intentar obtener el cuerpo de la respuesta
            try:
                error_data = response.json()  # Si el cuerpo es JSON
                error_message = error_data.get("error", "Error desconocido del servicio")
            except ValueError:
                error_message = response.text  # Si el cuerpo no es JSON

            if response.status_code == 403:
                error_message = "API Key inválida o no autorizada."
            elif response.status_code == 429:
                error_message = "Has alcanzado el límite de solicitudes para tu API Key."
            elif response.status_code == 400:
                error_message = f"Error 400, solicitud errónea. Respuesta del servicio: {error_message}"
            else:
                error_message = f"Error {response.status_code}: {response.reason}. Respuesta del servicio: {error_message}"

            return render_template("error.html", error_message=error_message)

        except Exception as err:
            error_message = f"Ocurrió un error inesperado: {err}"
            return render_template("error.html", error_message=error_message)

    return render_template("service_form.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error_message="Página no encontrada (404)."), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5010)
from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("FOREX_API_KEY")

@app.route("/")
def index():
    return jsonify({
        "mensaje": "API funcionando",
        "endpoint": "/tipo-cambio"
    })


@app.route("/tipo-cambio")
def tipo_cambio():
    try:
        url = f"https://api.fastforex.io/fetch-all?api_key={API_KEY}"
        response = requests.get(url)
        data = response.json()
        results = data.get("results", {})

        return jsonify({
            "USD_EUR": results.get("EUR"),
            "USD_PEN": results.get("PEN"),
            "USD_USD": results.get("USD"),
            "fuente": "fastFOREX"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handler(event, context):
    # Zappa needs this handler
    from flask import Response
    return app(event, context)


if __name__ == "__main__":
    app.run(debug=True)

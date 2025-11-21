from flask import Flask, jsonify
import pymysql
import os

app = Flask(__name__)

# Leer variables de entorno (Lambda)
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

# Conexión a RDS
def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def home():
    return {"mensaje": "API de Vehículos funcionando correctamente"}

@app.route("/vehiculos")
def obtener_vehiculos():
    conn = get_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM vehiculos")
            data = cursor.fetchall()
            return jsonify(data)

# Necesario para Lambda (Zappa)
def handler(event, context):
    from flask import Response
    return app(event, context)

if __name__ == "__main__":
    app.run(debug=True)

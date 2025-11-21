Laboratorio 07 – Servicios AWS
Introducción

Este laboratorio tiene como propósito desarrollar dos aplicaciones utilizando Python y Flask, para luego desplegarlas en AWS Lambda mediante Zappa. La primera aplicación consulta un API externo para obtener el tipo de cambio. La segunda aplicación muestra un catálogo de vehículos almacenados en una base de datos alojada en AWS RDS. El laboratorio evalúa el uso simultáneo de Flask, API externas, bases de datos remotas y servicios serverless en AWS.

El presente documento detalla todos los pasos realizados, desde la preparación del entorno local hasta el despliegue exitoso en AWS Lambda, incluyendo el código, configuraciones, ejecución, y una explicación clara de lo que se desplaza realmente hacia Lambda.

Preparación del Entorno

Antes de iniciar con cada pregunta, se realizó la preparación del entorno de desarrollo.

1. Crear carpeta del proyecto y entorno virtual
mkdir lab07
cd lab07
python -m venv venv


Activación:

Windows:

venv\Scripts\activate


Linux/Mac:

source venv/bin/activate

2. Instalación de dependencias necesarias
pip install flask requests pymysql zappa

3. Archivo de configuración de Zappa

Zappa será el encargado de empaquetar y desplegar el proyecto a AWS Lambda.

Pregunta 1
Aplicación Flask para mostrar el tipo de cambio
Descripción

Se desarrolla una aplicación Flask que consulta los tipos de cambio utilizando el servicio externo fastFOREX. Los valores obtenidos se devuelven en formato JSON a través del endpoint /tipo-cambio. La clave del API es manejada mediante una variable de entorno.

Código utilizado para la Pregunta 1
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
    from flask import Response
    return app(event, context)


if __name__ == "__main__":
    app.run(debug=True)

Variable de entorno necesaria

Para ejecutar correctamente el código se requiere:

Nombre: FOREX_API_KEY
Valor: clave de acceso al API fastFOREX.

Configuración local
setx FOREX_API_KEY "TU_API_KEY"

Configuración en AWS Lambda

AWS Lambda → Configuration → Environment Variables

Agregar:

FOREX_API_KEY

Ejecución local para pruebas
python app.py


Endpoints disponibles:

http://127.0.0.1:5000/

http://127.0.0.1:5000/tipo-cambio

Pregunta 2
Aplicación Flask con base de datos en AWS RDS
Descripción

La aplicación Flask de esta pregunta se conecta a una instancia MySQL creada en AWS RDS. El endpoint /vehiculos devuelve toda la información almacenada en la tabla vehiculos.

Código utilizado para la Pregunta 2
from flask import Flask, jsonify
import pymysql
import os

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

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

def handler(event, context):
    from flask import Response
    return app(event, context)

if __name__ == "__main__":
    app.run(debug=True)

Configuración de AWS RDS
Creación de instancia MySQL

Ingresar a AWS RDS.

Crear instancia MySQL en Free Tier.

Publicly Accessible: YES.

Configuración de seguridad: puerto 3306 abierto para desarrollo.

Conexión desde CMD
mysql -h <endpoint> -u admin -p


Ejemplo:

mysql -h database-carros.c2t8s644cm11.us-east-1.rds.amazonaws.com -u admin -p

Creación de base de datos y tabla
CREATE DATABASE vehiculosDB;
USE vehiculosDB;

CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    anio INT,
    precio DECIMAL(12,2)
);


Se insertaron 40 vehículos previamente definidos.

Variables de entorno configuradas en AWS Lambda
Variable	Descripción
DB_HOST	Endpoint de RDS
DB_USER	admin (o usuario configurado)
DB_PASSWORD	contraseña del RDS
DB_NAME	vehiculosDB
FOREX_API_KEY	clave del API fastFOREX (solo P1)
Despliegue en AWS Lambda utilizando Zappa
Inicialización de Zappa
zappa init


Respuestas recomendadas:

Stage: dev

App function: app.app

Región: us-east-1

Despliegue
zappa deploy dev


Zappa empaqueta:

Código Python

Librerías instaladas

Handler

Configuración del entorno

Luego crea:

Una función Lambda

Una API REST en API Gateway

Roles IAM necesarios

Actualización del despliegue
zappa update dev

Eliminación del despliegue
zappa undeploy dev

Detalle completo de lo que se desplaza a AWS Lambda

Esta sección describe explícitamente qué se transfirió a Lambda en el despliegue:

1. Código fuente del proyecto

Lambda recibe:

app.py (la aplicación Flask)

Handler generado para comunicar Flask con API Gateway

Código de dependencias utilizadas (Flask, requests, pymysql, etc.)

2. Dependencias del entorno virtual

Zappa detecta e incluye el contenido de:

venv/lib/pythonX.X/site-packages/


Esto garantiza que Lambda pueda ejecutar correctamente la aplicación sin dependencias externas.

3. Configuración de runtime

Lambda almacena:

Variables de entorno (DB_HOST, DB_USER, FOREX_API_KEY, etc.)

Configuración del handler

Asignación del tiempo máximo de ejecución

Regiones y permisos IAM

4. Creación automática de API Gateway

Zappa genera una API REST con rutas:

/dev/

/dev/tipo-cambio

/dev/vehiculos

Dependiendo del proyecto desplegado.

5. Logs y monitoreo en CloudWatch

Cada invocación:

Queda registrada

Permite depurar errores

Muestra conexiones al API externo (P1) y a RDS (P2)

Verificación del despliegue

Se verificó que:

La función Lambda se creó correctamente.

API Gateway expuso las rutas públicas.

Los endpoints devolvieron resultados correctos.

La conexión con fastFOREX funcionó en Pregunta 1.

La conexión a RDS devolvió los vehículos en Pregunta 2.

Las variables de entorno fueron reconocidas en Lambda.

Conclusiones

Se implementaron correctamente dos aplicaciones Flask con funcionalidades distintas.

Se utilizó una API externa para obtener datos de tipo de cambio.

Se configuró y consumió una base de datos MySQL en AWS RDS.

Se desplegaron ambas aplicaciones en AWS Lambda utilizando Zappa.

Se comprendió el funcionamiento del modelo serverless y la interacción entre Lambda, RDS y API Gateway.

Se documentó el proceso completo, cumpliendo todos los requisitos del laboratorio.

from flask import Flask # importamos la clase flask

app = Flask(__name__)  # creamos una instancia de la clase **

@app.route("/") # es un decorador que indica la raíz del sitio
def hello_world():
    return "<p>Mi primer Web en Flask!</p>"
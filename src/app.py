from flask import Flask
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()


def create_app():
    """
    Crea y configura la aplicación Flask.
    
    Returns:
        Flask: Instancia de la aplicación Flask.
    """
    app = Flask(__name__)
    return app


# Instancia de la aplicación
app = create_app()

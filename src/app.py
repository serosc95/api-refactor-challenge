from flask import Flask


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

import os
from functools import wraps
from flask import request, jsonify


def get_valid_api_key() -> str:
    """
    Obtiene la API key válida desde variables de entorno.
    
    Returns:
        str: API key válida o cadena vacía si no está configurada.
    """
    return os.getenv('API_KEY', '')


def require_api_key(f):
    """
    Decorador para proteger endpoints con API Key.
    Requiere el header X-API-KEY en la petición.
    
    Args:
        f: Función o método a proteger.
    
    Returns:
        Función decorada que verifica la API key antes de ejecutar.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        valid_api_key = get_valid_api_key()
        
        # Verificar que se proporcionó la API key
        if not api_key:
            return jsonify({
                'error': 'API key requerida',
                'message': 'Debe proporcionar el header X-API-KEY'
            }), 401

        # Verificar que la API key está configurada en el servidor
        if not valid_api_key:
            return jsonify({
                'error': 'API key no configurada en el servidor',
                'message': 'El servidor no tiene configurada una API key válida. Contacte al administrador.'
            }), 500
        
        # Verificar que la API key es válida
        if api_key != valid_api_key:
            return jsonify({
                'error': 'API key inválida',
                'message': 'La API key proporcionada no es válida'
            }), 401
        
        # API key válida, continuar con la ejecución
        return f(*args, **kwargs)
    
    return decorated_function


def setup_api_key_auth(app):
    """
    Configura la autenticación por API key para toda la aplicación.
    Se puede usar como alternativa al decorador para proteger todos los endpoints.
    
    Args:
        app: Instancia de la aplicación Flask.
    """
    valid_api_key = get_valid_api_key()
    
    # Verificar que la API key está configurada
    if not valid_api_key:
        print("Error: API_KEY no configurada en variables de entorno. La autenticación es obligatoria.")
    
    @app.before_request
    def verify_api_key():
        # Excluir rutas de documentación
        if request.endpoint in ['docs']:
            return None
        
        # Verificar que la API key está configurada en el servidor
        if not valid_api_key:
            return jsonify({
                'error': 'API key no configurada en el servidor',
                'message': 'El servidor no tiene configurada una API key válida. Contacte al administrador.'
            }), 500
        
        api_key = request.headers.get('X-API-KEY')
        
        if not api_key:
            return jsonify({
                'error': 'API key requerida',
                'message': 'Debe proporcionar el header X-API-KEY'
            }), 401
        
        if api_key != valid_api_key:
            return jsonify({
                'error': 'API key inválida',
                'message': 'La API key proporcionada no es válida'
            }), 401
        
        return None

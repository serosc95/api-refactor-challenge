from flask import jsonify
from flask.views import MethodView
from src.s3_client import get_s3_client
from src.auth import require_api_key


class DownloadView(MethodView):
    """
    Vista para obtener URLs prefirmadas de archivos desde S3 por clave.
    """
    
    @require_api_key
    def get(self, file_key: str = None):
        """
        Obtiene una URL prefirmada para descargar un archivo desde S3 usando su clave.
        Protegido con API key.
        
        Args:
            file_key (str): Clave del archivo en S3 (opcional, puede venir como query param).
        
        Returns:
            JSON: URL prefirmada o error 404 si el archivo no existe.
        """
        from flask import request
        
        # Obtener file_key de query params si no viene en la ruta
        if not file_key:
            file_key = request.args.get('file_key')
        
        if not file_key:
            return jsonify({'error': 'file_key es requerido'}), 400
        
        # Obtener tiempo de expiración
        expiration = request.args.get('expiration', default=3600, type=int)
        
        try:
            s3_client = get_s3_client()
            presigned_url = s3_client.get_presigned_url_by_key(file_key, expiration)
            
            if presigned_url is None:
                return jsonify({
                    'error': 'Archivo no encontrado',
                    'file_key': file_key
                }), 404
            
            return jsonify({
                'file_key': file_key,
                'download_url': presigned_url,
                'expires_in': expiration,
                'expires_in_hours': expiration / 3600
            }), 200
            
        except Exception as e:
            print(f"Error obteniendo URL prefirmada para '{file_key}': {e}")
            return jsonify({
                'error': 'Error al generar URL de descarga',
                'message': str(e)
            }), 500


class DownloadByNameView(MethodView):
    """
    Vista para obtener URLs prefirmadas de archivos desde S3 por nombre.
    """
    
    @require_api_key
    def get(self, filename: str = None):
        """
        Obtiene una URL prefirmada para descargar un archivo desde S3 usando su nombre original.
        Protegido con API key.
        
        Args:
            filename (str): Nombre original del archivo (opcional, puede venir como query param).
        
        Returns:
            JSON: URL prefirmada o error 404 si el archivo no existe.
        """
        from flask import request
        
        # Obtener filename de query params si no viene en la ruta
        if not filename:
            filename = request.args.get('filename')
        
        if not filename:
            return jsonify({'error': 'filename es requerido'}), 400
        
        # Obtener tiempo de expiración
        expiration = request.args.get('expiration', default=3600, type=int)
        
        try:
            s3_client = get_s3_client()
            
            # Buscar la clave del archivo
            file_key = s3_client.find_file_key_by_name(filename)
            
            if file_key is None:
                return jsonify({
                    'error': 'Archivo no encontrado',
                    'filename': filename
                }), 404
            
            # Generar URL prefirmada
            presigned_url = s3_client.get_presigned_url_by_key(file_key, expiration)
            
            if presigned_url is None:
                return jsonify({
                    'error': 'Error al generar URL de descarga',
                    'filename': filename,
                    'file_key': file_key
                }), 500
            
            return jsonify({
                'filename': filename,
                'file_key': file_key,
                'download_url': presigned_url,
                'expires_in': expiration,
                'expires_in_hours': expiration / 3600
            }), 200
            
        except Exception as e:
            print(f"Error obteniendo URL prefirmada para '{filename}': {e}")
            return jsonify({
                'error': 'Error al generar URL de descarga',
                'message': str(e)
            }), 500

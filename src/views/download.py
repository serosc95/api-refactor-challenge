from flask import Response
from flask.views import MethodView
from src.s3_client import get_s3_client


class DownloadView(MethodView):
    """
    Vista para descargar archivos desde S3.
    """
    
    def get(self, file_key: str = None):
        """
        Descarga un archivo desde S3 usando su clave.
        
        Args:
            file_key (str): Clave del archivo en S3 (opcional, puede venir como query param).
        
        Returns:
            Response: Archivo descargado o error 404.
        """
        from flask import request
        
        # Obtener file_key de query params si no viene en la ruta
        if not file_key:
            file_key = request.args.get('file_key')
        
        if not file_key:
            return {'error': 'file_key es requerido'}, 400
        
        try:
            s3_client = get_s3_client()
            file_content = s3_client.download_file_by_key(file_key)
            
            if file_content is None:
                return {'error': f'Archivo no encontrado: {file_key}'}, 404
            
            # Determinar content type basado en la extensión
            import os
            _, ext = os.path.splitext(file_key.lower())
            content_types = {
                '.csv': 'text/csv',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.xls': 'application/vnd.ms-excel',
                '.txt': 'text/plain',
                '.json': 'application/json',
                '.pdf': 'application/pdf',
            }
            content_type = content_types.get(ext, 'application/octet-stream')            
            filename = os.path.basename(file_key)
            
            return Response(
                file_content,
                mimetype=content_type,
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )
            
        except Exception as e:
            print(f"Error descargando archivo '{file_key}': {e}")
            return {'error': f'Error al descargar archivo: {str(e)}'}, 500


class DownloadByNameView(MethodView):
    """
    Vista para descargar archivos desde S3 por nombre.
    """
    
    def get(self, filename: str = None):
        """
        Descarga un archivo desde S3 usando su nombre original.
        
        Args:
            filename (str): Nombre original del archivo (opcional, puede venir como query param).
        
        Returns:
            Response: Archivo descargado o error 404.
        """
        from flask import request
        
        # Obtener filename de query params si no viene en la ruta
        if not filename:
            filename = request.args.get('filename')
        
        if not filename:
            return {'error': 'filename es requerido'}, 400
        
        try:
            s3_client = get_s3_client()
            file_content = s3_client.download_file_by_name(filename)
            
            if file_content is None:
                return {'error': f'Archivo no encontrado: {filename}'}, 404
            
            # Determinar content type basado en la extensión
            import os
            _, ext = os.path.splitext(filename.lower())
            content_types = {
                '.csv': 'text/csv',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.xls': 'application/vnd.ms-excel',
                '.txt': 'text/plain',
                '.json': 'application/json',
                '.pdf': 'application/pdf',
            }
            content_type = content_types.get(ext, 'application/octet-stream')
            
            return Response(
                file_content,
                mimetype=content_type,
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )
            
        except Exception as e:
            print(f"Error descargando archivo por nombre '{filename}': {e}")
            return {'error': f'Error al descargar archivo: {str(e)}'}, 500

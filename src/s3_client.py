import os
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from io import BytesIO
from typing import Optional
from datetime import datetime, timedelta
import uuid


class S3Client:
    """
    Cliente S3 para subir y descargar archivos.
    Todos los archivos se almacenan bajo la ruta: minerva_archive/testing/
    """
    
    BASE_PATH = "minerva_archive/testing"
    
    def __init__(self):
        """
        Inicializa el cliente S3 usando variables de entorno.
        
        Variables de entorno requeridas:
        - AWS_ACCESS_KEY_ID: Clave de acceso AWS (o 'test' para LocalStack)
        - AWS_SECRET_ACCESS_KEY: Clave secreta AWS (o 'test' para LocalStack)
        - AWS_REGION: Región AWS (default: 'us-east-1')
        - AWS_ENDPOINT_URL: URL del endpoint S3 (opcional, para LocalStack)
        - S3_BUCKET_NAME: Nombre del bucket S3
        """
        self.access_key = os.getenv('AWS_ACCESS_KEY_ID', 'test')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.endpoint_url = os.getenv('AWS_ENDPOINT_URL', None)
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'aresmaterials-test')
        
        # Configurar cliente S3
        config = {
            'aws_access_key_id': self.access_key,
            'aws_secret_access_key': self.secret_key,
            'region_name': self.region,
        }
        
        if self.endpoint_url:
            config['endpoint_url'] = self.endpoint_url
        
        self.s3_client = boto3.client('s3', **config)
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """
        Verifica que el bucket existe, si no, intenta crearlo.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                # Bucket no existe, intentar crearlo
                try:
                    if self.endpoint_url:
                        # LocalStack: no necesita LocationConstraint
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        # AWS real: necesita LocationConstraint
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    print(f"Bucket '{self.bucket_name}' creado exitosamente")
                except ClientError as create_error:
                    print(f"Error creando bucket '{self.bucket_name}': {create_error}")
            else:
                print(f"Error verificando bucket '{self.bucket_name}': {e}")
    
    def _generate_file_key(self, filename: str) -> str:
        """
        Genera una clave única para el archivo en S3.
        
        Args:
            filename (str): Nombre original del archivo.
        
        Returns:
            str: Clave completa del archivo en S3 (minerva_archive/testing/...)
        """
        # Generar ID único y timestamp
        file_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Extraer extensión del archivo
        _, ext = os.path.splitext(filename)
        
        file_key = f"{self.BASE_PATH}/{timestamp}_{file_id}{ext}"
        return file_key
    
    def upload_file(self, file_obj, filename: str) -> Optional[str]:
        """
        Sube un archivo a S3 bajo la ruta minerva_archive/testing/.
        
        Args:
            file_obj: Objeto de archivo (BytesIO, StringIO, o archivo de Flask).
            filename (str): Nombre original del archivo.
        
        Returns:
            str o None: Clave del archivo en S3 (file_key) o None si hay error.
        """
        try:
            # Generar clave única para el archivo
            file_key = self._generate_file_key(filename)
            
            # Si es StringIO, convertir a bytes
            if hasattr(file_obj, 'read'):
                # Resetear posición del archivo
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                
                # Leer contenido
                if isinstance(file_obj, BytesIO):
                    file_content = file_obj.read()
                else:
                    # StringIO u otro tipo
                    content = file_obj.read()
                    if isinstance(content, str):
                        file_content = content.encode('utf-8')
                    else:
                        file_content = content
            else:
                file_content = file_obj
            
            content_type = self._get_content_type(filename)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type
            )
            
            print(f"Archivo '{filename}' subido exitosamente a S3: {file_key}")
            return file_key
            
        except ClientError as e:
            print(f"Error de AWS al subir archivo '{filename}': {e}")
            return None
        except BotoCoreError as e:
            print(f"Error de boto3 al subir archivo '{filename}': {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al subir archivo '{filename}': {e}")
            return None
    
    def download_file_by_key(self, file_key: str) -> Optional[bytes]:
        """
        Descarga un archivo de S3 usando su clave completa.
        
        Args:
            file_key (str): Clave completa del archivo en S3.
        
        Returns:
            bytes o None: Contenido del archivo o None si hay error.
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            file_content = response['Body'].read()
            print(f"Archivo descargado exitosamente de S3: {file_key}")
            return file_content
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchKey':
                print(f"Archivo no encontrado en S3: {file_key}")
            else:
                print(f"Error de AWS al descargar archivo '{file_key}': {e}")
            return None
        except BotoCoreError as e:
            print(f"Error de boto3 al descargar archivo '{file_key}': {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al descargar archivo '{file_key}': {e}")
            return None
    
    def download_file_by_name(self, filename: str) -> Optional[bytes]:
        """
        Busca y descarga un archivo de S3 por su nombre original.
        Nota: Esta función busca en todos los archivos bajo minerva_archive/testing/
        y retorna el más reciente que coincida con el nombre.
        
        Args:
            filename (str): Nombre original del archivo.
        
        Returns:
            bytes o None: Contenido del archivo o None si no se encuentra.
        """
        try:
            # Listar objetos en el prefijo
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.BASE_PATH
            )
            
            if 'Contents' not in response:
                print(f"No se encontraron archivos en {self.BASE_PATH}")
                return None
            
            # Buscar archivos que terminen con el nombre buscado
            matching_files = []
            for obj in response['Contents']:
                key = obj['Key']
                # Extraer nombre del archivo de la clave
                stored_filename = os.path.basename(key)
                # Comparar sin extensión para mayor flexibilidad
                if filename in stored_filename or stored_filename.endswith(filename):
                    matching_files.append((obj['LastModified'], key))
            
            if not matching_files:
                print(f"Archivo '{filename}' no encontrado en S3")
                return None
            
            # Ordenar por fecha de modificación (más reciente primero)
            matching_files.sort(key=lambda x: x[0], reverse=True)
            
            # Descargar el más reciente
            latest_key = matching_files[0][1]
            return self.download_file_by_key(latest_key)
            
        except ClientError as e:
            print(f"Error de AWS al buscar archivo '{filename}': {e}")
            return None
        except BotoCoreError as e:
            print(f"Error de boto3 al buscar archivo '{filename}': {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al buscar archivo '{filename}': {e}")
            return None
    
    def file_exists(self, file_key: str) -> bool:
        """
        Verifica si un archivo existe en S3.
        
        Args:
            file_key (str): Clave completa del archivo en S3.
        
        Returns:
            bool: True si el archivo existe, False en caso contrario.
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                return False
            print(f"Error verificando existencia del archivo '{file_key}': {e}")
            return False
        except Exception as e:
            print(f"Error inesperado verificando archivo '{file_key}': {e}")
            return False
    
    def get_presigned_url_by_key(self, file_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Genera una URL prefirmada para descargar un archivo de S3 por su clave.
        
        Args:
            file_key (str): Clave completa del archivo en S3.
            expiration (int): Tiempo de expiración en segundos (default: 3600 = 1 hora).
        
        Returns:
            str o None: URL prefirmada o None si el archivo no existe o hay error.
        """
        try:
            # Verificar que el archivo existe
            if not self.file_exists(file_key):
                print(f"Archivo no encontrado en S3: {file_key}")
                return None
            
            # Generar URL prefirmada
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            
            print(f"URL prefirmada generada para: {file_key}")
            return url
            
        except ClientError as e:
            print(f"Error de AWS al generar URL prefirmada para '{file_key}': {e}")
            return None
        except BotoCoreError as e:
            print(f"Error de boto3 al generar URL prefirmada para '{file_key}': {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al generar URL prefirmada para '{file_key}': {e}")
            return None
    
    def find_file_key_by_name(self, filename: str) -> Optional[str]:
        """
        Busca la clave de un archivo en S3 por su nombre original.
        Retorna la clave del archivo más reciente que coincida.
        
        Args:
            filename (str): Nombre original del archivo.
        
        Returns:
            str o None: Clave del archivo o None si no se encuentra.
        """
        try:
            # Listar objetos en el prefijo
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.BASE_PATH
            )
            
            if 'Contents' not in response:
                print(f"No se encontraron archivos en {self.BASE_PATH}")
                return None
            
            # Buscar archivos que coincidan con el nombre
            matching_files = []
            for obj in response['Contents']:
                key = obj['Key']
                stored_filename = os.path.basename(key)
                # Comparar nombres (flexible con extensión)
                if filename in stored_filename or stored_filename.endswith(filename):
                    matching_files.append((obj['LastModified'], key))
            
            if not matching_files:
                print(f"Archivo '{filename}' no encontrado en S3")
                return None
            
            # Ordenar por fecha de modificación (más reciente primero)
            matching_files.sort(key=lambda x: x[0], reverse=True)            
            return matching_files[0][1]
            
        except ClientError as e:
            print(f"Error de AWS al buscar archivo '{filename}': {e}")
            return None
        except BotoCoreError as e:
            print(f"Error de boto3 al buscar archivo '{filename}': {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al buscar archivo '{filename}': {e}")
            return None
    
    def get_presigned_url_by_name(self, filename: str, expiration: int = 3600) -> Optional[str]:
        """
        Genera una URL prefirmada para descargar un archivo de S3 por su nombre original.
        
        Args:
            filename (str): Nombre original del archivo.
            expiration (int): Tiempo de expiración en segundos (default: 3600 = 1 hora).
        
        Returns:
            str o None: URL prefirmada o None si el archivo no existe o hay error.
        """
        # Buscar la clave del archivo
        file_key = self.find_file_key_by_name(filename)
        
        if not file_key:
            return None
        
        # Generar URL prefirmada
        return self.get_presigned_url_by_key(file_key, expiration)
    
    def _get_content_type(self, filename: str) -> str:
        """
        Determina el tipo de contenido basado en la extensión del archivo.
        
        Args:
            filename (str): Nombre del archivo.
        
        Returns:
            str: Tipo MIME del archivo.
        """
        _, ext = os.path.splitext(filename.lower())
        content_types = {
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.pdf': 'application/pdf',
        }
        return content_types.get(ext, 'application/octet-stream')


# Instancia global del cliente S3
_s3_client_instance = None


def get_s3_client() -> S3Client:
    """
    Obtiene la instancia singleton del cliente S3.
    
    Returns:
        S3Client: Instancia del cliente S3.
    """
    global _s3_client_instance
    if _s3_client_instance is None:
        _s3_client_instance = S3Client()
    return _s3_client_instance

import json
from flask.views import MethodView
from flask import request
from io import StringIO, BytesIO
from typing import Callable, Dict, Any, Optional
from src.s3_client import get_s3_client


class BaseFileProcessingView(MethodView):
    """
    Clase base que proporciona funcionalidad común para procesar archivos.
    """
    
    FILES_KEY = 'files[]'
    FILE_READER = 'stringio'
    REQUIRES_FORM = True
    
    def get_files_list(self, key: Optional[str] = None) -> list:
        """
        Obtiene la lista de archivos del request.
        
        Args:
            key (str, optional): Clave del formulario. Si no se proporciona, usa FILES_KEY.

        Returns:
            list: Lista de archivos.
        """
        key = key or self.FILES_KEY
        return request.files.getlist(key)
    
    def get_form_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos del formulario.
        
        Returns:
            dict: Datos del formulario.
        """
        return request.form
    
    def read_file(self, file) -> Any:
        """
        Lee un archivo y lo convierte según la configuración de FILE_READER.
        
        Args:
            file: Archivo de Flask.
        
        Returns:
            StringIO o BytesIO según la configuración.
        """
        if self.FILE_READER == 'bytesio':
            return BytesIO(file.read())
        return StringIO(file.read().decode('utf-8'))
    
    def extract_file_params(self, filename: str, form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae parámetros específicos del formulario para un archivo.
        Debe ser implementado en subclases para definir qué parámetros extraer.
        
        Args:
            filename (str): Nombre del archivo.
            form (dict): Datos del formulario.
        
        Returns:
            dict: Parámetros extraídos del formulario.
        
        Raises:
            NotImplementedError: Si no se implementa en la subclase.
        """
        raise NotImplementedError("Las subclases deben implementar extract_file_params")
    
    def build_helper_args(self, file_data: Any, filename: str, form_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construye los argumentos para la función helper.
        Debe ser implementado en subclases para definir cómo construir los argumentos.
        
        Args:
            file_data: Datos del archivo (StringIO o BytesIO).
            filename (str): Nombre del archivo.
            form_params (dict): Parámetros extraídos del formulario.
        
        Returns:
            dict: Argumentos para la función helper.
        
        Raises:
            NotImplementedError: Si no se implementa en la subclase.
        """
        raise NotImplementedError("Las subclases deben implementar build_helper_args")
    
    def get_helper_function(self) -> Callable:
        """
        Retorna la función helper a usar para procesar los archivos.
        Debe ser implementado en subclases.
        
        Returns:
            callable: Función helper.
        
        Raises:
            NotImplementedError: Si no se implementa en la subclase.
        """
        raise NotImplementedError("Las subclases deben implementar get_helper_function")
    
    def process_single_file(self, file, form: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Procesa un archivo individual y lo guarda en S3.
        
        Args:
            file: Archivo de Flask.
            form (dict): Datos del formulario.
        
        Returns:
            dict o None: Resultado del procesamiento con file_key de S3 o None si hay error.
        """
        try:
            filename = file.filename
            if not filename:
                print("Error: Archivo sin nombre")
                return None
            
            # Guardar archivo original en S3 antes de procesar
            file_key = None
            try:
                s3_client = get_s3_client()
                # Resetear posición del archivo para leerlo completo
                file.seek(0)
                file_key = s3_client.upload_file(file, filename)
                if not file_key:
                    print(f"Advertencia: No se pudo subir '{filename}' a S3, continuando con procesamiento local")
            except Exception as e:
                print(f"Error subiendo archivo '{filename}' a S3: {e}. Continuando con procesamiento local")
            
            # Extraer parámetros del formulario
            if self.REQUIRES_FORM:
                try:
                    form_params = self.extract_file_params(filename, form)
                except Exception as e:
                    print(f"Error extrayendo datos del formulario para {filename}: {e}")
                    return None
            else:
                form_params = {}
            
            # Leer archivo según configuración (resetear posición nuevamente)
            try:
                file.seek(0)
                file_data = self.read_file(file)
            except Exception as e:
                print(f"Error leyendo archivo {filename}: {e}")
                return None
            
            # Construir argumentos para la función helper
            try:
                helper_args = self.build_helper_args(file_data, filename, form_params)
            except Exception as e:
                print(f"Error construyendo argumentos para {filename}: {e}")
                return None
            
            # Llamar a la función helper
            try:
                helper_func = self.get_helper_function()
                result = helper_func(**helper_args)
                
                # Agregar información de S3 al resultado
                if result and isinstance(result, dict):
                    result['s3_file_key'] = file_key
                    result['s3_uploaded'] = file_key is not None
                
                return result
            except Exception as e:
                print(f"Error procesando archivo {filename}: {e}")
                return None
                
        except Exception as e:
            print(f"Error general procesando archivo: {e}")
            return None
    
    def post(self) -> str:
        """
        Método POST generalizado que procesa múltiples archivos.
        
        Returns:
            str: JSON con los resultados del procesamiento.
        """
        form = self.get_form_data() if self.REQUIRES_FORM else {}
        files = self.get_files_list()
        results = []
        
        for file in files:
            result = self.process_single_file(file, form)
            if result is not None:
                results.append(result)
        
        return json.dumps(results)

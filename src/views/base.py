import json
from flask.views import MethodView
from flask import request
from io import StringIO, BytesIO


class BaseFileProcessingView(MethodView):
    """
    Clase base que proporciona funcionalidad común para procesar archivos.
    """
    
    def get_files_list(self, key='files[]'):
        """
        Obtiene la lista de archivos del request.
        
        Args:
            key (str): Clave del formulario para obtener los archivos.
                      Por defecto 'files[]', pero puede ser 'files' para DSC.
        
        Returns:
            list: Lista de archivos.
        """
        return request.files.getlist(key)
    
    def get_form_data(self):
        """
        Obtiene los datos del formulario.
        
        Returns:
            dict: Datos del formulario.
        """
        return request.form
    
    def process_files(self, process_file_func):
        """
        Procesa múltiples archivos usando una función de procesamiento.
        
        Args:
            process_file_func (callable): Función que procesa un archivo individual.
                                         Debe aceptar (file, filename, form) y retornar un resultado.
        
        Returns:
            str: JSON con los resultados del procesamiento.
        """
        form = self.get_form_data()
        files = self.get_files_list()
        results = []
        
        for file in files:
            try:
                result = process_file_func(file, form)
                if result is not None:
                    results.append(result)
            except Exception as e:
                print(f"Error procesando archivo {file.filename if file else 'desconocido'}: {e}")
                continue
        
        return json.dumps(results)
    
    def read_file_as_stringio(self, file):
        """
        Lee un archivo y lo convierte a StringIO.
        
        Args:
            file: Archivo de Flask.
        
        Returns:
            StringIO: Objeto StringIO con el contenido del archivo.
        """
        return StringIO(file.read().decode('utf-8'))
    
    def read_file_as_bytesio(self, file):
        """
        Lee un archivo y lo convierte a BytesIO.
        
        Args:
            file: Archivo de Flask.
        
        Returns:
            BytesIO: Objeto BytesIO con el contenido del archivo.
        """
        return BytesIO(file.read())

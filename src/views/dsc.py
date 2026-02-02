from .base import BaseFileProcessingView
from helpers import find_tg_from_dsc


class DscView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas DSC.
    """
    
    FILES_KEY = 'files'
    REQUIRES_FORM = False
    
    def extract_file_params(self, filename: str, form: dict) -> dict:
        """
        DSC no requiere parámetros del formulario.
        
        Args:
            filename (str): Nombre del archivo.
            form (dict): Datos del formulario (no usado).
        
        Returns:
            dict: Diccionario vacío.
        """
        return {}
    
    def build_helper_args(self, file_data, filename: str, form_params: dict) -> dict:
        """
        Construye los argumentos para find_tg_from_dsc.
        
        Args:
            file_data: StringIO con los datos del archivo.
            filename (str): Nombre del archivo.
            form_params (dict): Parámetros del formulario (no usado).
        
        Returns:
            dict: Argumentos para la función helper.
        """
        return {
            'file': file_data,
            'filename': filename,
        }
    
    def get_helper_function(self):
        """
        Retorna la función helper para procesar archivos DSC.
        
        Returns:
            callable: Función find_tg_from_dsc.
        """
        return find_tg_from_dsc

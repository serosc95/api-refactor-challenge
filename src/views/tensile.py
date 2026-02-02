from .base import BaseFileProcessingView
from helpers import get_mechanical_properties


class TensileView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas de tracción.
    """
    
    def extract_file_params(self, filename: str, form: dict) -> dict:
        """
        Extrae parámetros específicos del formulario para pruebas de tracción.
        
        Args:
            filename (str): Nombre del archivo.
            form (dict): Datos del formulario.
        
        Returns:
            dict: Parámetros extraídos.
        """
        return {
            'label': form[f'label_{filename}'],
            'model': form['model'],
            'thickness': float(form[f'thickness_{filename}']) * 0.001,  # micro to milimeters
            'height': float(form[f'height_{filename}']),  # milimeters
            'width': float(form[f'width_{filename}']),  # milimeters
        }
    
    def build_helper_args(self, file_data, filename: str, form_params: dict) -> dict:
        """
        Construye los argumentos para get_mechanical_properties.
        
        Args:
            file_data: StringIO con los datos del archivo.
            filename (str): Nombre del archivo.
            form_params (dict): Parámetros del formulario.
        
        Returns:
            dict: Argumentos para la función helper.
        """
        return {
            'file': file_data,
            'filename': filename,
            'label': form_params['label'],
            'thickness': form_params['thickness'],
            'height': form_params['height'],
            'width': form_params['width'],
            'mark10_model': form_params['model'],
        }
    
    def get_helper_function(self):
        """
        Retorna la función helper para procesar archivos de tracción.
        
        Returns:
            callable: Función get_mechanical_properties.
        """
        return get_mechanical_properties

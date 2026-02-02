from .base import BaseFileProcessingView
from helpers import get_cte_alpha_values


class CteView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas CTE.
    """
    
    def extract_file_params(self, filename: str, form: dict) -> dict:
        """
        Extrae parámetros específicos del formulario para pruebas CTE.
        
        Args:
            filename (str): Nombre del archivo.
            form (dict): Datos del formulario.
        
        Returns:
            dict: Parámetros extraídos.
        """
        return {
            'label': form[f'label_{filename}'],
            'total_cycles': int(form[f'total_cycles_{filename}']),
            'target_cycles': int(form[f'target_cycles_{filename}']),
            'tg': float(form[f'tg_{filename}']) if form[f'tg_{filename}'] else None,
        }
    
    def build_helper_args(self, file_data, filename: str, form_params: dict) -> dict:
        """
        Construye los argumentos para get_cte_alpha_values.
        
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
            'estimated_tg': form_params['tg'],
            'total_cycles': form_params['total_cycles'],
            'target_cycles': form_params['target_cycles'],
        }
    
    def get_helper_function(self):
        """
        Retorna la función helper para procesar archivos CTE.
        
        Returns:
            callable: Función get_cte_alpha_values.
        """
        return get_cte_alpha_values

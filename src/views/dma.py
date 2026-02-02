from .base import BaseFileProcessingView
from helpers import get_dma_properties_from_file


class DmaView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas DMA.
    """
    
    def extract_file_params(self, filename: str, form: dict) -> dict:
        """
        Extrae parámetros específicos del formulario para pruebas DMA.
        
        Args:
            filename (str): Nombre del archivo.
            form (dict): Datos del formulario.
        
        Returns:
            dict: Parámetros extraídos.
        """
        return {
            'label': form[f'label_{filename}'],
        }
    
    def build_helper_args(self, file_data, filename: str, form_params: dict) -> dict:
        """
        Construye los argumentos para get_dma_properties_from_file.
        
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
        }
    
    def get_helper_function(self):
        """
        Retorna la función helper para procesar archivos DMA.
        
        Returns:
            callable: Función get_dma_properties_from_file.
        """
        return get_dma_properties_from_file

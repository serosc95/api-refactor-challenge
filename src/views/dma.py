from .base import BaseFileProcessingView
from helpers import get_dma_properties_from_file
import json


class DmaView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas DMA.
    """
    
    def post(self):
        """
        Procesa archivos de pruebas DMA.
        
        Returns:
            str: JSON con los resultados del procesamiento.
        """
        form = self.get_form_data()
        files = self.get_files_list("files[]")
        results = []
        
        for file in files:
            try:
                filename = file.filename
                label = form[f'label_{filename}']
                stringio_data = self.read_file_as_stringio(file)
            except Exception as e:
                print(f"Error extrayendo datos del formulario para {filename}: {e}")
                continue
            
            try:
                results.append(get_dma_properties_from_file(stringio_data, filename, label))
            except Exception as e:
                print(f"Error procesando archivo {filename}: {e}")
        
        return json.dumps(results)

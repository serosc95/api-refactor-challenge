from .base import BaseFileProcessingView
from helpers import find_tg_from_dsc
import json


class DscView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas DSC.
    """
    
    def post(self):
        """
        Procesa archivos de pruebas DSC.
        
        Returns:
            str: JSON con los resultados del procesamiento.
        """
        files = self.get_files_list("files")
        results = []
        
        for file in files:
            try:
                filename = file.filename
                stringio_data = self.read_file_as_stringio(file)
            except Exception as e:
                print(f"Error extrayendo datos del formulario para {filename}: {e}")
                continue
            
            try:
                result = find_tg_from_dsc(stringio_data, filename)
                results.append(result)
            except Exception as e:
                print(f"Error procesando archivo {filename}: {e}")
        
        return json.dumps(results)

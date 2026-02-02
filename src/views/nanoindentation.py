from .base import BaseFileProcessingView
from helpers import get_properties_from_nanoindentation_file
import json


class NanoindentationView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas de nanoindentación.
    """
    
    def post(self):
        """
        Procesa archivos de pruebas de nanoindentación.
        
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
                bytesio_data = self.read_file_as_bytesio(file)
            except Exception as e:
                print(f"Error extrayendo datos del formulario para {filename}: {e}")
                continue
            
            try:
                result = get_properties_from_nanoindentation_file(
                    file=bytesio_data, filename=filename, label=label,
                )
                results.append(result)
                print('Nano results', results)
            except Exception as e:
                print(f"Error procesando archivo {filename}: {e}")
        
        return json.dumps(results)

from .base import BaseFileProcessingView
from helpers import get_cte_alpha_values
import json


class CteView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas CTE.
    """
    
    def post(self):
        """
        Procesa archivos de pruebas CTE.
        
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
                total_cycles = int(form[f'total_cycles_{filename}'])
                target_cycles = int(form[f'target_cycles_{filename}'])
                tg = float(form[f'tg_{filename}']) if form[f'tg_{filename}'] else None
            except Exception as e:
                print(f"Error extrayendo datos del formulario para {filename}: {e}")
                continue
            
            try:
                results.append(get_cte_alpha_values(
                    file=stringio_data, filename=filename, label=label,
                    estimated_tg=tg, total_cycles=total_cycles, target_cycles=target_cycles,
                ))
            except Exception as e:
                print(f"Error procesando archivo {filename}: {e}")
        
        return json.dumps(results)

from .base import BaseFileProcessingView
from helpers import get_mechanical_properties


class TensileView(BaseFileProcessingView):
    """
    Vista para procesar archivos de pruebas de tracción.
    """
    
    def post(self):
        """
        Procesa archivos de pruebas de tracción.
        
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
                model = form['model']
                stringio_data = self.read_file_as_stringio(file)
                thickness = float(form[f'thickness_{filename}']) * 0.001  # micro to milimeters
                height = float(form[f'height_{filename}'])  # milimeters
                width = float(form[f'width_{filename}'])  # milimeters
            except Exception as e:
                print(f"Error extrayendo datos del formulario para {filename}: {e}")
                continue
            
            try:
                results.append(get_mechanical_properties(
                    file=stringio_data, filename=filename, label=label,
                    thickness=thickness, height=height, width=width, mark10_model=model,
                ))
            except Exception as e:
                print(f"Error procesando archivo {filename}: {e}")
        
        # Upload to S3
        import json
        return json.dumps(results)

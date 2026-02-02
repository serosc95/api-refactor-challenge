#
# App Views
#
import json
from flask.views import MethodView
from flask import Flask, request
from io import StringIO, BytesIO
from helpers import (
    get_mechanical_properties, get_adhesion_info,
    get_cte_alpha_values, get_properties_from_nanoindentation_file,
    get_dma_properties_from_file, find_tg_from_dsc
    
)

app = Flask(__name__)

#
# Tensile Test
#
class TensileView(MethodView):   
    def post(self):
        form = request.form
        files = request.files.getlist("files[]")
        results = []        
        
        for file in files:
            try:
                filename = file.filename
                label = form[f'label_{filename}']
                model = form['model']
                stringio_data = StringIO(file.read().decode('utf-8'))
                thickness = float(form[f'thickness_{filename}'])*0.001 # micro to mili -meters
                height = float(form[f'height_{filename}']) # milimeters
                width = float(form[f'width_{filename}']) # milimeters
            except Exception as e:
                continue
            
            try:
                results.append(get_mechanical_properties(
                    file=stringio_data, filename=filename, label=label,
                    thickness=thickness, height=height, width=width, mark10_model=model,
                ))
            except Exception as e:
                print(e)
                
        # Upload to S3
        return json.dumps(results)
app.add_url_rule('/tensile',view_func=TensileView.as_view("tensile"), methods=['GET','POST'] )

#
# CTE
#
class CteView(MethodView):
    
    def post(self):
        form = request.form
        files = request.files.getlist("files[]")
        results = []
        
        for file in files:
            try:
                filename = file.filename
                label = form[f'label_{filename}']
                files_str = file.read().decode('utf-8')
                stringio_data = StringIO(files_str)
                total_cycles = int(form[f'total_cycles_{filename}']) # unitless 1
                target_cycles = int(form[f'target_cycles_{filename}']) # unitless 1
                tg = float(form[f'tg_{filename}']) if form[f'tg_{filename}'] else None # celsius
            except Exception as e:
                print(e)
                continue
            
            try:
                results.append(get_cte_alpha_values(
                    file=stringio_data, filename=filename, label=label,
                    estimated_tg=tg, total_cycles=total_cycles, target_cycles=target_cycles,
                ))
            except Exception as e:
                print(e)
        return json.dumps(results)
app.add_url_rule('/cte',view_func=CteView.as_view("cte"), methods=['GET','POST'] )

#
# Nanoindentation
#
class NanoindentationView(MethodView):
    
    def post(self):
        form = request.form
        files = request.files.getlist("files[]")
        results = []
        
        for file in files:
            try:
                filename = file.filename
                label = form[f'label_{filename}']
                bytesio_data = BytesIO(file.read())
            except Exception as e:
                print(e)
                continue
            
            try:
                results.append(get_properties_from_nanoindentation_file(
                    file=bytesio_data, filename=filename, label=label,
                ))
                print('Nano results',results)
            except Exception as e:
                print(e)
        return json.dumps(results)
app.add_url_rule('/nanoindentation',view_func=NanoindentationView.as_view("nanoindentation"), methods=['GET','POST'] )

#
# DMA
#
class DmaView(MethodView):
    
    def post(self):
        form = request.form
        files = request.files.getlist("files[]")
        results = []
        for file in files:
            filename = file.filename
            label = form[f'label_{filename}']
            stringio_data = StringIO(file.read().decode('utf-8'))
            
            try:
                results.append(get_dma_properties_from_file(stringio_data, filename, label))
            except Exception as e:
                print(e)        
        return json.dumps(results)                    
app.add_url_rule('/dma',view_func=DmaView.as_view("dma"), methods=['GET','POST'] )

#
# DSC
#
class DscView(MethodView):
    
    def post(self):
        mode = 'read'
        files = request.files.getlist("files")
        results = []
        for file in files:
            filename = file.filename
            stringio_data = StringIO(file.read().decode('utf-8'))
            
            try:
                result = find_tg_from_dsc(stringio_data, filename)
                results.append(result)
            except Exception as e:
                print(e)
app.add_url_rule('/dsc',view_func=DscView.as_view("dsc"), methods=['GET','POST'] )
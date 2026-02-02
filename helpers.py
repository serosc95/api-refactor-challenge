import numpy as np
import pandas as pd

def get_mechanical_properties(file, filename, label,
                              thickness=0.075, height=100., width=5., sigma=18,
                              yield_empirical_offset=0.002, mark10_model='F105',
                              with_uuids=True):
    '''
    INPUT:
        file (strIO)
        filename (str)
        thickness (float): milimeters
        height (float): milimeters
        width (float): milimeters
        sigma (int): An empirical filtering parameter
    OUTPUT:
        thickness (float): micrometers
        height (float): milimeters
        width (float): milimeters
        young_modulus (float): gigapascal
    '''
    _, load, distance, time = np.genfromtxt(file, unpack=True, skip_header=17)
    return {
        'filename':filename,
        'label':label,
        'height':round(float(height), 4),
        'width':round(float(width), 4),
        'thickness': round(float(thickness)*1000, 4),
        'avg_thickness': None, # Este es solo para new Mark10
        'young_modulus':None,
        'strength':None,
        'break_strain':None,
        'toughness':None,
        'yield_strength':None,
        'yield_strain':None,
        'resilience':None,
        'data_loss':None,
        'plot_data': {
        	'strain':[],
        	'stress':[],
        	'initial_strain':[],
        	'initial_stress':[],
        	'young_modulus_strain_reference': None,
        },
    }
    
def get_adhesion_info(file, filename, label, sample_width_in_cm=2.4):
    '''
    INPUT:
        filename (strIO)
        sample_width_in_cm (float) centimeters
    OUTPUT:
        average_load (float): Newtons
        peel_strength (float): gf/in
    '''
    _, load, travel, _ = np.genfromtxt(file, unpack=True,skip_header=7)
    return {
        'filename': filename,
        'label':label,
        'width':sample_width_in_cm,
        'peel_strength': None,
        'average_load': None,
        'plot_data': {
            'load':load.tolist(),
            'travel':travel.tolist(),
        }
    }
    
def get_cte_alpha_values(file, filename, label, estimated_tg=None, total_cycles=2, target_cycles=2):
    '''
    INPUT:
        file (strIO): data stringIO
        filename (str)
        estimated_tg (float|None): When None, tg estimation is calculated. Runtime increases.
        total_cycles (int): Number of cycles on the TMA run. SOP indicates 2.
        target_cycles (int): Starting at 1, number of the cycle in which CTEs are calculated
    '''
    time,raw_temperature,dimension_change,raw_dimension_change_normalized = np.genfromtxt(file, unpack=True, skip_header=9, delimiter=',')
    return {
        'filename':filename,
        'label':label,
        'alpha_1': None,
        'alpha_2':None,
        'estimated_tg':None,
        'plot_data': {
            'temperature':[],
            'dimension_change_normalized':[],
            'glassy_fit_line':{
                'temperature':[],
                'fitted_line':[],
            },
            'rubbery_fit_line':{
                'temperature':[],
                'fitted_line':[],
            }
        }
    }

def get_properties_from_nanoindentation_file(file, filename, label):
    '''
    INPUT 
        file (BytesIO)

    OUTPUT 
        results (dict).
            contains a dict of properties and list of pairs of lists for plotting depth,load curves.
    '''
    data = pd.read_excel(file,sheet_name='Results',index_col=0)
    return {
        'filename':filename,
        'label':label,
        'martens_hardness_avg':None, # Gpa
        'martens_hardness_std':None, # Gpa
        'depth_avg':None, # mm
        'depth_std':None, # mm
        'modulus_avg':None, # GPa
        'modulus_std':None, # GPa
        'plot_data':[]
    }

def get_dma_properties_from_file(file, filename, label):
    '''
    INPUT 
        file (strIO)
    '''
    angular_frequency,step_time,temperature,oscillation_strain,oscillation_stress,tan_delta,storage_modulus,loss_modulus,stiffness = np.genfromtxt(file,skip_header=15,unpack=True,dtype=None,encoding=None,delimiter=',')
    return {
        'tg':None,
        'storage_modulus_reference_temperature':None,
        'storage_modulus_value':None,
        'rubbery_modulus_reference_temperature':None,
        'rubbery_modulus_value':None,
        'full_width_half_maximum':None,
        'loss_modulus_peak_temperature':None,
        'plot_data': {
            'temperature':temperature.tolist(),
            'tan_delta':tan_delta.tolist(),
            'storage_modulus':storage_modulus.tolist(),
            'loss_modulus':loss_modulus.tolist(),
            'tg_start':None,
            'tg_end':None,
            'loss_modulus_peak_temperature':None,
        }
    }

def find_tg_from_dsc(file, filename):
    time,temperature,heat_flow = np.loadtxt(file,delimiter=',',unpack=True,skiprows=10)
    return {
        'filename':filename,
        'tg':None,
        'plot_data': {
            'temperature':temperature.tolist(),
            'heat_flow':heat_flow.tolist()
        }
    }


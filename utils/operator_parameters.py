from snapista import Operator
import json


def operator_parameters(operator_name):
    # returns a dictionary of the operator's parameters and values

    operator = Operator(operator_name)
    return operator._params


def list_to_operator_dict(used_operators):
    op_params_dict = {}
    for op in used_operators:
        op_params = operator_parameters(op)
        op_params_dict[op] = op_params

    return op_params_dict


def add_suffix_parameter(op_params_dict, operator_suffixes):

    for op in op_params_dict:
        if op in operator_suffixes:
            if operator_suffixes[op] != '':  # passes if its Read or Write which have empty strings as suffixes
                op_params_dict[op]['suffix'] = operator_suffixes[op]
        else:
            op_params_dict[op]['suffix'] = 'null_suffix'

    return op_params_dict


def dict_to_json(my_dict):
    my_json = json.dumps(my_dict, indent = 4)

    return my_json


# def create_graph():

#     return g


if __name__ == '__main__':
    # given a list of operator names, a dictionary is created with the operators parameters and default values
    # the operators suffix is then added to the dictionary and this is converted into json and saved in preprocessing_jsons/operator_defaults.json
    
    # TO DO: just have the dictionary with the operators and suffixes instead of the list and add the suffixes when adding the other params
    # TO DO: move these functions into the helpers file?

    # test_op = Operator('BandMaths')
    # test_op.describe()
    # exit()

    used_operators = ['Read', 'Write', 'Subset', 'Remove-GRD-Border-Noise', 'ThermalNoiseRemoval', 'Apply-Orbit-File', 'Calibration', 'Speckle-Filter', 'Multilook', 'Terrain-Flattening', 'Terrain-Correction', 'LinearToFromdB', 'TOPSAR-Deburst', 'TOPSAR-Split', 'BandMaths']
    operator_suffixes = {
        'Read': '',
        'Write': '',
        'Subset': 'Sub',
        'Remove-GRD-Border-Noise': 'BNR',
        'ThermalNoiseRemoval': 'TNR',
        'Apply-Orbit-File': 'Orb',
        'Calibration': 'Cal',
        'Speckle-Filter': 'Spkl',
        'Multilook': 'ML',
        'Terrain-Flattening': 'TF',
        'Terrain-Correction': 'TC',
        'LinearToFromdB': 'dB',
        'TOPSAR-Deburst': 'DB',
        'TOPSAR-Split': 'Split',
        'BandMaths': 'BM'
    }

    # creating a dictionary of operators and their params
    operators_dict = list_to_operator_dict(used_operators)
    # print(operators_dict)

    # adding the suffix parameter to the operators
    operators_dict = add_suffix_parameter(operators_dict, operator_suffixes)

    operators_json = dict_to_json(operators_dict)
    # print(operators_json)

    # writing these to the operator_defaults.json file
    with open('./preprocessing_jsons/operator_defaults.json', 'w') as f:
        f.write(operators_json)


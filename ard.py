# just try processing one of the UK scenes to calibrated and compare to snap process
# recreate todays process?
# recreate a non-AM fiji scene as catapult did

'''
TO DO:
-[DONE] create basic graoh 
-[DONE] try to run it 
-[DONE] compare output to snap [compared in SNAP and have identical pixel values]
-[DONE] make all into functions
-try to setup reading from json
-try to read input from zip file? (will still require checking the manifest.safe exists)
-[DONE] rerun to compare to snap
-use try/execpts
-add logging
-move functions into utils dir
-try adding option to clear temp dir
-create a seperate file with all the snapista operators in default mode?
-try with user input/diff parameters (via json object?)
-[DONE] to set the operators from json, can you loop through the operators given parameters in the json and set them like that?
-create dockerfile - with snap and snapista, rememebr to deactivate conda base env before testing
-make into a RESTful API in Django
-define a json of default values for each operator?
-add basic validation checks (if zip provided, if parameters have valid values - else use defaults)
-design basic react frontend for users to choose parameters (where to load/save the input/output?)
-adapt for open access hub download
-read the SNAP descriptions of what each operator does (and document)
'''

from snapista import Operator, OperatorParams
from snapista import Graph
from pathlib import Path
import zipfile
import json

# from snapista import TargetBand, TargetBandDescriptors
# Graph.list_operators()
# Graph.describe_operators() 


def find_scene_zip(scene):
    # checking if there is a zip file present
    zip_path = Path(f'./input/{scene}.zip')

    if not zip_path.is_file():
        print('No zip file found for this scene')  # MAKE INTO LOGS
        print('exiting process')
        exit()
    else: 
        print(f'zip file present for scene {scene}')
        print('proceeding...')
        return


def unzip_scene_file(scene, manifest_path):
        # unzipping the file into the temp dir if no manifest safe is present yet
    print('not manifest file found in temp directory')
    print(f'unzipping {scene}.zip into temp directory')

    # MAKE INTO FUNCTION
    with zipfile.ZipFile(f'./input/{scene}.zip', 'r') as zip_ref:
        zip_ref.extractall('./temp/')

    print(manifest_path.is_file())


def find_manifest_file(scene):
    # checks if there is already access to the manifest.safe file => else need to unzip file
    manifest_path = Path(f'./temp/{scene}.SAFE/manifest.safe')

    if not manifest_path.is_file():
        # unzipping the scene file
        unzip_scene_file(scene, manifest_path)

        if manifest_path.is_file():
            print(f'{scene}.zip unzipped into temp directory')
            print(f'manifest safe file present: {manifest_path.is_file()}')
            print('proceeding...')
            return
        else:
            print(f'manifest.safe file could not be found in the unzipped: {scene}.zip file')
            print('exiting process')
            exit()
    else:
        print('manifest file already present in temp directory')
        print('proceeding...')
        return


def output_file_name(scene):

    with open('./utils/ard.json', 'r') as f:
        operators = json.load(f)
        suffix = ''

        for operator in operators:
            if 'suffix' in operators[operator]:
                suffix += f"_{operators[operator]['suffix']}"
        
        output_name = f'{scene}{suffix}.dim'
    return output_name


def set_operator_params(current_operator):
    with open('./utils/ard.json', 'r') as f:
        operators = json.load(f)

        # FILE AND OUPUT FILE PARAMS NEED TO BE SET PROPERLY (updated in the json at some point?)

        if current_operator in operators:
            # create instance for that operator
            op_name = current_operator.capitalize().replace('-', '_')  # 'Apply-Orbit-File' => apply_orbit_file
            print(str(current_operator))
            op_object = Operator(str(current_operator))  # creating the instance of the operator

            print(f'setting params for: {current_operator}')
            for param in operators[current_operator]:
                if param != 'suffix':
                    print(f'setting the {param} paramater for {current_operator} to: {operators[current_operator][param]}')
                    setattr(op_object, param, operators[current_operator][param])  # setting the paramater for the operator

            return op_name, op_object  # returns the name of the operator and the object itself
        else:
            print('operator not found in json file')
            print('exiting process')
            exit()


def create_graph():

    g = Graph()

    with open('./utils/ard.json', 'r') as f:
        operators = json.load(f)
        source = None

        for operator in operators:
            op_name, op_object = set_operator_params(operator)
            g.add_node(operator=op_object, 
                       node_id=op_name, 
                       source=source)
            source = op_name
    
    return g


def update_json(input_scene, output_scene):
    with open('./utils/ard.json', 'r') as f:
        operators = json.load(f)

    operators['Read']['file'] = input_scene
    operators['Write']['file'] = output_scene
    
    with open('./utils/ard.json', 'w') as f:
        json.dump(operators, f, indent=4)

    return


def prepare_ard(scene):

    scene = 'S1A_IW_GRDH_1SDV_20170724T174037_20170724T174100_017616_01D7A7_F0DA'
    # params =  # json file of parameters
    # output name =  # call a FUNCTION to abbreviate each operator to build the output name   

    # checks if a zip file is present in the setup input dir for the scene 
    find_scene_zip(scene)
    print('zip file exists')

    # checks the manifest file is avaliable and makes so if possible
    find_manifest_file(scene)
    print('manifest file exists')

    # sets name of output file
    output_name = output_file_name(scene)
    output_scene = f'./output/{output_name}'
    print(f'output file name set to: {output_name}')

    # defining the input file
    input_scene = f'./temp/{scene}.SAFE/manifest.safe'  # location of where the manifest.safe file is confirmed to be
    print(f'input file set to: {input_scene}')

    # updating the json file with the input file name output name
    update_json(input_scene, output_scene)
    print('proceeding to processing graph')

    # TO DO: define all the operators and params in a seperate file
    # OR can the below be setup purely with loops and using the json input?
    print('creating processing graph')
    g = create_graph()
    print('processing graph created')

    print('running processing graph')
    g.run()
    print('processing graph ran')
    print('Your output file is in your set output directory')


# --- function called on main
'''
first input must be the manifest.SAFE file, then dims
    -take the scene name as an input, name of graph to use, and an optional json file of parameters
    -looks in input folder for any file matching the scene name (fine if its zip or SAFE, else fails)
    -the operators the user chooses will determine the output file's name
-the final write operator needs to have GeoTiff output? - include if statement for the default of the Write's type parameter
'''

if __name__ == '__main__':
    prepare_ard('S1A_IW_GRDH_1SDV_20170724T174037_20170724T174100_017616_01D7A7_F0DA')  # should take json file as argument?

    # name of scene to process
    # json of operators and parameters (to be taken from user input in future)
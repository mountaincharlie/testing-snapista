from snapista import Operator
from snapista import Graph
from pathlib import Path
import zipfile
import json
import logging


def setup_logger():

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel("DEBUG")

    return logger


def find_scene_zip(scene, input_dir):
    # checking if there is a zip file present
    zip_path = Path(f'{input_dir}{scene}.zip')

    if not zip_path.is_file():
        logging.info('No zip file found for this scene')  # MAKE INTO LOGS
        logging.info('exiting process')
        exit()
    else: 
        logging.info(f'zip file present for scene {scene}')
        return


def unzip_scene_file(scene, manifest_path, input_dir, temp_dir):
        # unzipping the file into the temp dir if no manifest safe is present yet
    logging.info('not manifest file found in temp directory')
    logging.info(f'unzipping {scene}.zip into temp directory')

    # MAKE INTO FUNCTION
    with zipfile.ZipFile(f'{input_dir}{scene}.zip', 'r') as zip_ref:
        zip_ref.extractall(f'{temp_dir}')

    logging.info(manifest_path.is_file())
    return


def find_manifest_file(scene, input_dir, temp_dir):
    # checks if there is already access to the manifest.safe file => else need to unzip file
    manifest_path = Path(f'{temp_dir}{scene}.SAFE/manifest.safe')

    if not manifest_path.is_file():
        # unzipping the scene file
        unzip_scene_file(scene, manifest_path, input_dir, temp_dir)

        if manifest_path.is_file():
            logging.info(f'{scene}.zip unzipped into temp directory')
            logging.info(f'manifest safe file present: {manifest_path.is_file()}')
            return
        else:
            logging.info(f'manifest.safe file could not be found in the unzipped: {scene}.zip file')
            logging.info('exiting process')
            exit()
    else:
        logging.info('manifest file already present in temp directory')
        return


def output_file_name(scene, ard_json_path):

    # with open('./utils/ard.json', 'r') as f:
    with open(ard_json_path, 'r') as f:
        operators = json.load(f)
        suffix = ''

        for operator in operators:
            if 'suffix' in operators[operator]:
                suffix += f"_{operators[operator]['suffix']}"
        
        output_name = f'{scene}{suffix}.dim'
    return output_name


def set_operator_params(current_operator, ard_json_path):
    with open(ard_json_path, 'r') as f:
        operators = json.load(f)

        # FILE AND OUPUT FILE PARAMS NEED TO BE SET PROPERLY (updated in the json at some point?)

        if current_operator in operators:
            # create instance for that operator
            op_name = current_operator.capitalize().replace('-', '_')  # 'Apply-Orbit-File' => apply_orbit_file
            logging.info(str(current_operator))
            op_object = Operator(str(current_operator))  # creating the instance of the operator

            logging.info(f'setting params for: {current_operator}')
            for param in operators[current_operator]:
                if param != 'suffix':
                    # logging.info(f'setting the {param} paramater for {current_operator} to: {operators[current_operator][param]}')
                    setattr(op_object, param, operators[current_operator][param])  # setting the paramater for the operator

            return op_name, op_object  # returns the name of the operator and the object itself
        else:
            logging.info('operator not found in json file')
            logging.info('exiting process')
            exit()


def create_graph(ard_json_path):

    g = Graph()

    with open(ard_json_path, 'r') as f:
        operators = json.load(f)
        source = None

        for operator in operators:
            op_name, op_object = set_operator_params(operator, ard_json_path)
            g.add_node(operator=op_object, 
                       node_id=op_name, 
                       source=source)
            source = op_name
    
    return g


def update_json(input_scene, output_scene, ard_json_path):
    with open(ard_json_path, 'r') as f:
        operators = json.load(f)

    operators['Read']['file'] = input_scene
    operators['Write']['file'] = output_scene
    
    with open(ard_json_path, 'w') as f:
        json.dump(operators, f, indent=4)

    return

from snapista import Operator
from snapista import Graph
from snapista import TargetBand
from snapista import TargetBandDescriptors
from pathlib import Path
import zipfile
import json
import logging
import os
import glob
import imghdr


def setup_logger():
    # setting up the logger to DEBUG level
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel("DEBUG")
    
    # reducing the messages recieved from rasterio
    logging.getLogger("rasterio").setLevel("INFO")
    logging.getLogger("rasterio._io").setLevel("INFO")

    return logger


def find_scene_zip(scene, input_dir):
    # checking if there is a zip file present for the scene

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

    # TO DO: maek into function?
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
    # creating the output file name based on the operator suffixes from the json file

    # TO DO: if bandmaths is in the graph => need to include which bands are being used in the output name

    with open(ard_json_path, 'r') as f:
        operators = json.load(f)
        suffix = ''

        for operator in operators:
            if 'suffix' in operators[operator]:
                suffix += f"_{operators[operator]['suffix']}"
        
        output_name = f'{scene}{suffix}'  # remove file time, it will be added automatically?
    return output_name


def set_operator_params(current_operator, ard_json_path):
    # setting the parameters for an operator from the provided json file

    with open(ard_json_path, 'r') as f:
        operators = json.load(f)

        # TO DO: make seperate andmaths handling function
        if current_operator == 'BandMaths':
            # creates BandMaths operator
            op_object = Operator(str(current_operator))

            # using list comprehension to create the band descriptors for each of the bands in the 'targetBands' 
            band_descriptors = [
                TargetBand(
                    name=band,
                    type=operators[current_operator]['targetBandDescriptors'].get('type'),
                    expression=operators[current_operator]['targetBandDescriptors'].get('expression'),
                    description=operators[current_operator]['targetBandDescriptors'].get('description'),
                    unit=operators[current_operator]['targetBandDescriptors'].get('unit'),
                    no_data_value=operators[current_operator]['targetBandDescriptors'].get('no_data_value')
                ) for band in operators[current_operator]['targetBands'].split(',')
            ]  

            setattr(op_object, 'targetBandDescriptors', TargetBandDescriptors(band_descriptors))

            return current_operator, op_object # returns the name of the operator and the object itself

        # create instance for that operator if its in the json file
        if current_operator in operators:
            # converting names e.g. 'Apply-Orbit-File' => apply_orbit_file
            op_name = current_operator.capitalize().replace('-', '_')
            op_object = Operator(str(current_operator))

            logging.info(f'setting params for: {current_operator}')
            for param in operators[current_operator]:
                if param != 'suffix':
                    # logging.info(f'setting the {param} paramater for {current_operator} to: {operators[current_operator][param]}')
                    # setting the paramater for the operator
                    setattr(op_object, param, operators[current_operator][param])  

            return op_name, op_object  # returns the name of the operator and the object itself
        else:
            logging.info('operator not found in json file')
            logging.info('exiting process')
            exit()


def create_graph(ard_json_path):
    # creates the graph based on the operators and parameters defined in provided json file

    g = Graph()

    # set path to your local version of SNAP (v9) or defaults to conda version installed with Snapista (v8)
    g.gpt_path = os.getenv('SNAP_GPT', '/home/spatialdaysubuntu/anaconda3/envs/snapista_env/snap/bin/gpt')
    logging.info(f'path to snap gpt being used: {g.gpt_path}')

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


def update_json_filenames(input_scene, output_scene, ard_json_path):
    # updates the json file with the input and output file names

    with open(ard_json_path, 'r') as f:
        operators = json.load(f)

    operators['Read']['file'] = input_scene
    operators['Write']['file'] = output_scene
    
    with open(ard_json_path, 'w') as f:
        json.dump(operators, f, indent=4)

    return


def find_external_dem(ext_dem, static_dir):
    # checks if the external dem is present in the static directory

    ext_dem_path = f'{static_dir}{ext_dem}.tif'

    if Path(ext_dem_path).is_file():
        logging.info(f'external dem found: {ext_dem_path}')
        return ext_dem_path
    else:
        logging.info(f'external dem not found: {ext_dem_path}')
        logging.info('exiting process')
        exit()


def update_json_ext_dem(ext_dem_path, ard_json_path):
    # checks if the TF and TC operators are present and correctly configures the parameters for using external dems

    ops_to_update = ['Terrain-Flattening', 'Terrain-Correction']

    with open(ard_json_path, 'r') as f:
        operators = json.load(f)
    
    for op in ops_to_update:
        if op in operators:
            operators[op]['demName'] = 'External DEM'
            operators[op]['externalDEMFile'] = ext_dem_path
            operators[op]['externalDEMNoDataValue'] = "-32768.0"
            operators[op]['externalDEMApplyEGM'] = "true"
            
    with open(ard_json_path, 'w') as f:
        json.dump(operators, f, indent=4)

    return

# just try processing one of the UK scenes to calibrated and compare to snap process
# recreate todays process?
# recreate a non-AM fiji scene as catapult did

'''
TO DO:
-[DONE] create basic graoh 
-[DONE] try to run it 
-[DONE] compare output to snap [compared in SNAP and have identical pixel values]
-[DONE] make all into functions
-[DONE] rerun to compare to snap
-[DONE] add logging
-[DONE] try to setup reading from json set as an argument for the main function
-[DONE] move functions into utils dir
-[DONE] to set the operators from json, can you loop through the operators given parameters in the json and set them like that?
-retest with the functions in helper file
-finish creating the json file for catapults ard process (with snap dem)
-workout handling using an external dem 
-create dockerfile - with snap and snapista, rememebr to deactivate conda base env before testing
-use try/execpts
-try to read input from zip file? (will still require checking the manifest.safe exists)
-try adding option to clear temp dir
-create a seperate file with all the snapista operators in default mode?
-try with user input/diff parameters (via json object?)
-make into a RESTful API in Django [setup python environment first]
-define a json of default values for each operator?
-add basic validation checks (if zip provided, if parameters have valid values - else use defaults)
-design basic react frontend for users to choose parameters (where to load/save the input/output?)
-adapt for open access hub download [add function and option in main function call to download from open access hub if not present]
-read the SNAP descriptions of what each operator does (and document)
'''

# from snapista import Operator, OperatorParams
# from snapista import Graph
# from pathlib import Path
# import zipfile
# import json
import logging
from utils.helpers import *

# from snapista import TargetBand, TargetBandDescriptors
# Graph.list_operators()
# Graph.describe_operators()

# Set up the logger
logger = setup_logger()


def prepare_ard(scene, ard_json_path):

    scene = 'S1A_IW_GRDH_1SDV_20170724T174037_20170724T174100_017616_01D7A7_F0DA'
    # params =  # json file of parameters
    # output name =  # call a FUNCTION to abbreviate each operator to build the output name   

    # checks if a zip file is present in the setup input dir for the scene 
    find_scene_zip(scene)
    logger.info('zip file exists, proceeding to find manifest.safe file')

    # checks the manifest file is avaliable and makes so if possible
    find_manifest_file(scene)
    logger.info('manifest file exists, proceeding to set input and output file names')

    # sets name of output file
    output_name = output_file_name(scene, ard_json_path)
    output_scene = f'./output/{output_name}'
    logger.info(f'output file name set to: {output_name}')

    # defining the input file
    input_scene = f'./temp/{scene}.SAFE/manifest.safe'  # location of where the manifest.safe file is confirmed to be
    logger.info(f'input file set to: {input_scene}')

    # updating the json file with the input file name output name
    update_json(input_scene, output_scene, ard_json_path)
    logger.info('proceeding to processing graph')

    # TO DO: define all the operators and params in a seperate file
    # OR can the below be setup purely with loops and using the json input?
    logger.info('creating processing graph')
    g = create_graph(ard_json_path)
    logger.info('processing graph created')

    logger.info('running processing graph')
    g.run()
    logger.info('processing graph ran')
    logger.info('Your output file is in your set output directory')


# --- function called on main
'''
first input must be the manifest.SAFE file, then dims
    -take the scene name as an input, name of graph to use, and an optional json file of parameters
    -looks in input folder for any file matching the scene name (fine if its zip or SAFE, else fails)
    -the operators the user chooses will determine the output file's name
-the final write operator needs to have GeoTiff output? - include if statement for the default of the Write's type parameter
'''

if __name__ == '__main__':
    prepare_ard('S1A_IW_GRDH_1SDV_20170724T174037_20170724T174100_017616_01D7A7_F0DA', './preprocessing_jsons/Orb_Cal_ard.json')  # take a json file name as an argument (e.g. Orb_Cal_ard.json, Orb_Cal_TC_ard.json etc)

    # name of scene to process
    # json of operators and parameters (to be taken from user input in future)
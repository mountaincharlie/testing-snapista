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
-[DONE] retest with the functions in helper file
-[DONE] create conda environmetn with snap, snapista, gdal and rasterio
-workout handling using an external dem
-why does the TF operator cause a section of the fiji scene ocean to be cut out (run a different scene)?
-why does the uk scene not process correctly?
-fix the gdal method for converting the final prduct to COG
-finish creating the json file for catapults ard process (with snap dem) and others from the table

-create dockerfile - with snap and snapista, rememebr to deactivate conda base env before testing
-try to make a fiji AM scene work with reprojections (output quality will need to be assessed)
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


from utils.helpers import *
from datetime import datetime

# Set up the logger/
logger = setup_logger()


def prepare_ard(scene, ard_json_path, input_dir='./input/', static_dir='./static/', temp_dir='./temp/', output_dir='./output/'):

    logger.info(f'processing scene: {scene}')
    logger.info(f'processing with json: {ard_json_path.split("/")[-1]}')
    logger.info(f'output directory set to: {output_dir}')  

    # checks if a zip file is present in the setup input dir for the scene 
    find_scene_zip(scene, input_dir)
    logger.info('zip file exists, proceeding to find manifest.safe file')

    # checks the manifest file is avaliable and makes so if possible
    find_manifest_file(scene, input_dir, temp_dir)
    logger.info('manifest file exists, proceeding to set input and output file names')

    # sets name of output file
    output_name = output_file_name(scene, ard_json_path)
    output_scene = f'{output_dir}{output_name}'
    logger.info(f'output file name set to: {output_name}')

    # defining the input file
    input_scene = f'{temp_dir}{scene}.SAFE/manifest.safe'  # location of where the manifest.safe file is confirmed to be
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
    process_start_time = datetime.now().strftime("%H:%M:%S")  
    logger.info(f'graph processing starting at: {process_start_time}')
    g.run()
    logger.info('processing graph ran')
    logger.info('Your output file is in your set output directory')
    process_finish_time = datetime.now().strftime("%H:%M:%S")  
    logger.info(f'graph processing finished at: {process_finish_time}')

    # converting the output into COG



def view_xml_graph_from_json(ard_json_path):

    g = create_graph(ard_json_path)

    return g.view()


# --- function called on main
'''
first input must be the manifest.SAFE file, then dims
    -take the scene name as an input, name of graph to use, and an optional json file of parameters
    -looks in input folder for any file matching the scene name (fine if its zip or SAFE, else fails)
    -the operators the user chooses will determine the output file's name
-the final write operator needs to have GeoTiff output? - include if statement for the default of the Write's type parameter
'''

if __name__ == '__main__':
    # view_xml_graph_from_json('./preprocessing_jsons/catapults_ard_snap_dem.json')
    prepare_ard('S1A_IW_GRDH_1SDV_20170724T174037_20170724T174100_017616_01D7A7_F0DA', './preprocessing_jsons/test_ard.json', './input/', './static/', './temp/', './output/')  # take a json file name as an argument (e.g. Orb_Cal_ard.json, Orb_Cal_TC_ard.json etc)

    # S1A_IW_GRDH_1SDV_20180104T062254_20180104T062319_020001_02211F_A294  - UK scene (mostly land)
    # S1A_IW_GRDH_1SDV_20230416T180636_20230416T180701_048125_05C928_0F6E  - UK scene (land/sea)
    # S1A_IW_GRDH_1SDV_20170724T174037_20170724T174100_017616_01D7A7_F0DA  - Fiji scene



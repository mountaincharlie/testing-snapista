from utils.helpers import setup_logger
from utils.cog_helpers import output_to_cog
from datetime import datetime

# Set up the logger
logger = setup_logger()


if __name__ == '__main__':
    # converting a preprocessed scene to cog (args: output dir, cog dir, output file name)

    logger.info(f'cog processing starting at: {datetime.now().strftime("%H:%M:%S")}')

    output_to_cog('S1A_IW_GRDH_1SDV_20170724T174037_20170724T174100_017616_01D7A7_F0DA', './output/', './output/cogs/')
    
    logger.info(f'cog processing finished at: {datetime.now().strftime("%H:%M:%S")}')

    # S1A_IW_GRDH_1SDV_20180104T062254_20180104T062319_020001_02211F_A294  - UK scene (mostly land)
    # S1A_IW_GRDH_1SDV_20230416T180636_20230416T180701_048125_05C928_0F6E  - UK scene (land/sea)
    # S1A_IW_GRDH_1SDV_20170724T174037_20170724T174100_017616_01D7A7_F0DA  - Fiji scene
    # S1A_IW_GRDH_1SDV_20150508T072136_20150508T072201_005826_0077EE_7582  - Solomon scene
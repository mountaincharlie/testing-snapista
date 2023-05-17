from utils.helpers import setup_logger
import logging
import os
import glob
from osgeo import gdal
import rasterio
from rasterio.enums import Resampling
from rasterio.io import MemoryFile
from rasterio.shutil import copy
import numpy as np

# Set up the logger
logger = setup_logger()


def cog_translate(
        src_path,
        dst_path,
        dst_kwargs,
        indexes=None,
        nodata=None,
        alpha=None,
        overview_level=5,
        overview_resampling=None,
        config=None,
):
    """
    Create Cloud Optimized Geotiff.
    Parameters
    ----------
    src_path : str or PathLike object
        A dataset path or URL. Will be opened in "r" mode.
    dst_path : str or Path-like object
        An output dataset path or or PathLike object.
        Will be opened in "w" mode.
    dst_kwargs: dict
        output dataset creation options.
    indexes : tuple, int, optional
        Raster band indexes to copy.
    nodata, int, optional
        nodata value for mask creation.
    alpha, int, optional
        alpha band index for mask creation.
    overview_level : int, optional (default: 6)
        COGEO overview (decimation) level
    config : dict
        Rasterio Env options.
    """
    config = config or {}

    with rasterio.Env(**config):
        with rasterio.open(src_path) as src:

            indexes = indexes if indexes else src.indexes
            meta = src.meta
            meta["count"] = len(indexes)
            meta.pop("nodata", None)
            meta.pop("alpha", None)

            meta.update(**dst_kwargs)
            meta.pop("compress", None)
            meta.pop("photometric", None)

            with MemoryFile() as memfile:
                with memfile.open(**meta) as mem:
                    wind = list(mem.block_windows(1))
                    for ij, w in wind:
                        matrix = src.read(window=w, indexes=indexes)
                        mem.write(matrix, window=w)

                        if nodata is not None:
                            mask_value = (
                                    np.all(matrix != nodata, axis=0).astype(
                                        np.uint8
                                    )
                                    * 255
                            )
                        elif alpha is not None:
                            mask_value = src.read(alpha, window=w)
                        else:
                            mask_value = None
                        if mask_value is not None:
                            mem.write_mask(mask_value, window=w)

                    if overview_resampling is not None:
                        overviews = [2 ** j for j in range(1, overview_level + 1)]

                        mem.build_overviews(overviews, Resampling[overview_resampling])
                        mem.update_tags(
                            OVR_RESAMPLING_ALG=Resampling[overview_resampling].name.upper()
                        )

                    copy(mem, dst_path, copy_src_overviews=True, **dst_kwargs)


def cog_conversion(in_path, out_path, nodata=0):
    # setting default cog profile
    logging.info('COG CREATING STAGE')
    cog_profile = {
        'driver': 'GTiff',
        'interleave': 'pixel',
        'tiled': True,
        'blockxsize': 512,
        'blockysize': 512,
        'compress': 'DEFLATE',
        'predictor': 2,
        'zlevel': 9
    }

    cog_translate(
        in_path,
        out_path,
        cog_profile,
        overview_level=5,
        overview_resampling='average'
    )

    ds = gdal.Open(in_path, gdal.GA_Update)
    if ds is not None:
        b = ds.GetRasterBand(1)
        b.SetNoDataValue(nodata)
        b.FlushCache()
        b = None
        ds = None
    else:
        logging.info('not updated nodata')


def convert_to_cog(input_file, output_file, nodata=0):
    # checking if the COG already exists before converting to COG

    if os.path.exists(input_file):
        # ensure output cog doesn't already exist
        if not os.path.exists(output_file):
            cog_conversion(input_file, output_file, nodata=nodata)
        else:
            logging.info(f'cog already exists: {output_file}')
    else:
        logging.info(f'cannot find product: {input_file}')


def output_to_cog(output_name, output_dir='./output/', cog_dir='./output/cogs/'):
    """
    Convert S1 scene products to cogs [+ validate].
    """

    # checks if the output directory exists - TO DO: PUT in seperate dir checking/making function
    if not os.path.exists(output_dir):
        logging.info(f'Cannot find non-cog scene directory: {output_dir}')

    # creating cog scene directory - TO DO: replace with os.makedirs(exists_ok=True)?
    if not os.path.exists(cog_dir):
        logging.info(f'Creating scene cog directory: {cog_dir}')
        os.mkdir(cog_dir)

    # identifying which .img files to use for cog conversion
    prod_paths = glob.glob(output_dir + output_name + '*data/*.img')
    print('prod_paths: ', prod_paths)

    logging.info(f"ALL PROD_PATHS: {prod_paths}")

    # iterate over prods to create parellel processing list
    for prod in prod_paths:
        logging.info(f'the prod is: {prod}')
        out_filename = os.path.join(cog_dir, output_name + '_' + os.path.basename(prod)[:-4] + '.tif')  # - TO DO*****
        logging.info(f"converting {prod} to cog at {out_filename}")
        convert_to_cog(prod, out_filename, nodata=-9999)

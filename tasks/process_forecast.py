import os
import shutil
import time
import urllib
import numpy as np
from osgeo import gdal
from datetime import datetime, timedelta
from config.forecast_models import models


from app import celery
from flask import current_app

from config.models import ModelParams
from processing.utils import (
    check_new_zips,
    download_file_util,
    raster_2_binary,
    extract_rasters,
    create_template_raster,
    polygonize_raster
)

modelUrls = {
    "icon": "http://84.201.155.104/icon-ural/",
    "gfs": "http://84.201.155.104/gfs-ural/",
}


@celery.task(name="app.tasks.create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


# saved as sample celery task
@celery.task(name="app.tasks.download_file")
def download_file(zipName, model):
    dwnFld = current_app.config['DWN_FLD']

    baseUrl = models[model].DOWNLOAD_URL

    url = f'{baseUrl}/{zipName}.zip'

    save_path = os.path.join(dwnFld, model)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    save_path_zip = os.path.join(save_path, f'{zipName}.zip')
    with urllib.request.urlopen(url) as response, open(save_path_zip, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


@celery.task(name="app.tasks.check_new_files")
def process_new_files():
    dwnFld = current_app.config['DWN_FLD']
    outMaskFolder = current_app.config['MASK_FLD']
    outVektorFolder = current_app.config['VECTOR_FLD']
    processingHours = current_app.config['PROCESSING_HOURS']

    for modelName in models:

        modelParams: ModelParams = models[modelName]

        # TODO Refactor Huge nesting
        # generate list of necessary indicators for each models
        indicatorsForExtract = set()
        for eventGroup in modelParams.CALCULATIONS:
            for eventSubGroup in eventGroup.subgroups:
                for conditionGroup in eventSubGroup.condition_groups:
                    for condition in conditionGroup.conditions:
                        indicatorsForExtract.add(condition.index_name)

        url = modelParams.DOWNLOAD_URL
        modelDwnFld = os.path.join(dwnFld, modelName)
        # newZipNames = check_new_zips(url, modelDwnFld, startDate=datetime(2021, 7, 20))
        newZipNames = ['2021072100.zip']

        if len(newZipNames) == 0:
            current_app.logger.info(f'Not found new archives for model {modelName}')
            pass
            # return

        current_app.logger.info(f'For {modelName} found new archives {",".join(newZipNames)}')

        for zipName in newZipNames:
            archivePath = download_file_util(url, zipName, modelName)  # './2021051512.zip'
            archiveDate = os.path.basename(archivePath).split('.zip')[0]  # 2021051512
            forecastType = '00' if archiveDate.endswith('00') else '12'
            extractFolder = os.path.join(current_app.config['EXTRACT_FLD'], archiveDate)

            # check that folder exists
            listFolders = [extractFolder]
            for fld in listFolders:
                if not os.path.exists(fld):
                    os.mkdir(fld)

            extract_rasters(archivePath, extractFolder, indicatorsForExtract)

            for hour in processingHours:

                # squalls groups
                for eventGroup in modelParams.CALCULATIONS:

                    eventGroupName = eventGroup.name
                    eventGroupOut = []

                    # make true date
                    dateTimeObject = datetime.strptime(archiveDate, '%Y%m%d%H')
                    dateTimeObject = dateTimeObject + timedelta(hours=int(hour))
                    actualDate = dateTimeObject.strftime("%Y%m%d.%H")  # in UTC

                    # outRaster
                    outRasterPath = os.path.join(
                        outMaskFolder,
                        # f'{model}.{archiveDate}.{hour}.{eventGroupName}.{actualDate}.tif'  # original name
                        f'{modelName}.{actualDate}.{forecastType}.{eventGroupName}.tif'   # with true date
                    )
                    create_template_raster(
                        outRasterPath,
                        x_size=modelParams.RASTER_X_SIZE,
                        y_size=modelParams.RASTER_Y_SIZE,
                        geo_transform=modelParams.RASTER_GEO_TRANSFORM
                    )
                    ds = gdal.Open(outRasterPath, gdal.GA_Update)

                    for eventSubGroup in eventGroup.subgroups:

                        levelCode = eventSubGroup.level_code


                        conditions = []
                        for conditionGroup in eventSubGroup.condition_groups:
                            masks = []
                            for condition in conditionGroup.conditions:
                                # TODO Refactor format for input file
                                rasterName = f'{modelName}.{archiveDate}.0{hour}.{condition.index_name}.tif'
                                rasterPath = os.path.join(extractFolder, rasterName)
                                mask = raster_2_binary(rasterPath, condition.calculation)
                                masks.append(mask)

                            allSubConditions = np.stack(masks, axis=2)

                            # check that in each pixel all condition is true(1)
                            # if one condition is false in pixel wil be zero
                            # if all condition is true in pixel will be one
                            result = np.amin(allSubConditions, axis=2)
                            conditions.append(result)

                        # merged condition for one subgroup e.g. squall_L1
                        mergedCondition = np.stack(conditions, axis=2)
                        # we may have few condition for one subgroup. It means that
                        # for one subgroup may be few different condition groups
                        # and it may be detected by one or other condition group
                        # so, firstly we merge all subcondition together
                        # if at least in one pixel subcondition is true return 1
                        # if all subcondition is negative return 0
                        result = mergedCondition.any(axis=2).astype(np.uint8)
                        # replace selected value with subgroup code
                        result = np.where(result != 0, levelCode, 0)
                        eventGroupOut.append(result)

                    # select most danger group for each pixel
                    eventGroupOut = np.stack(eventGroupOut, axis=2)
                    # need mask for zero values
                    eventGroupOut = np.ma.masked_equal(eventGroupOut, 0.0)
                    eventGroupOut = eventGroupOut.min(axis=2)

                    ds.GetRasterBand(1).WriteArray(eventGroupOut.filled(fill_value=0))
                    ds = None

            # convert raster to vector
            for rasterName in os.listdir(outMaskFolder):
                inRasterPath = os.path.join(outMaskFolder, rasterName)

                vektorName = rasterName.replace('tif', 'geojson')

                outVektorPath = os.path.join(outVektorFolder, vektorName)
                polygonize_raster(inRasterPath, outVektorPath, 4326, frmt="GeoJSON")



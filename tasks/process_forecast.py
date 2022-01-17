import os
import shutil
import time
import urllib
from typing import List

import numpy as np
from osgeo import gdal
from datetime import datetime, timedelta
from config.used_models import models
from config.calculations import usedIndexes


from app import celery
from flask import current_app

from models.forecast_models import ModelParams
from processing.utils import (
    check_new_zips,
    download_file_util,
    raster_2_binary,
    extract_rasters,
    create_template_raster,
    polygonize_raster
)


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
    outVectorFolder = current_app.config['VECTOR_FLD']
    processingHours = current_app.config['PROCESSING_HOURS']
    startDateString = current_app.config['FIRST_ZIP_DATE']
    extractFolder = current_app.config['EXTRACT_FLD']

    for modelName in models:
        modelParams = models[modelName]

        newFiles = check_new_files(modelName, modelParams, startDateString, dwnFld)
        newFiles = ['2021081012.zip']
        newFiles = ['2021072100.zip']
        newDates = [x.split('.zip')[0] for x in newFiles]
        current_app.logger.info(f'checking new files end for model {modelName}')

        download_files(newFiles, modelName, modelParams, dwnFld)
        current_app.logger.info(f'downloading ends for model {modelName}')

        dwnModelFld = os.path.join(dwnFld, modelName)
        extract_files(newFiles, dwnModelFld, modelParams, extractFolder)
        current_app.logger.info(f'extracting ends for model {modelName}')

        created_masks = []
        for newDate in newDates:
            extractDateFolder = os.path.join(current_app.config['EXTRACT_FLD'], newDate)
            forecastType = '00' if newDate.endswith('00') else '12'
            for hour in processingHours:

                dateTimeObject = datetime.strptime(newDate, '%Y%m%d%H')
                dateTimeObject = dateTimeObject + timedelta(hours=int(hour))
                trueDateTime = dateTimeObject.strftime("%Y%m%d.%H")  # in UTC
                # так как прогнозные даты указаны с количеством часов вперед на которое прогнозируется
                # реальная дата прогноза может быть смещена вперед, поэтому ее надо рассчитывать реальный срок прогноза
                # gfs.2021072100.024.dls.tif -> gfs.2021072200.000.dls.tif
                # make true date
                rasterTrueDateTime = trueDateTime

                for group in modelParams.CALCULATIONS:

                    resultArray = group.calculation(extractDateFolder, newDate, hour)

                    rasterName = f'{modelName}.{forecastType}.{rasterTrueDateTime}.{group.name}.tif'
                    outRasterPath = os.path.join(outMaskFolder, rasterName)
                    create_template_raster(
                        outRasterPath,
                        modelParams.RASTER_X_SIZE,
                        modelParams.RASTER_Y_SIZE,
                        modelParams.RASTER_GEO_TRANSFORM
                    )

                    ds = gdal.Open(outRasterPath, gdal.GA_Update)
                    ds.GetRasterBand(1).WriteArray(resultArray)
                    ds = None

                    created_masks.append(rasterName)

        vectorize_rasters(created_masks, outMaskFolder, outVectorFolder)
        current_app.logger.info(f'vectorization ends for model {modelName}')


def check_new_files(modelName, modelParams: ModelParams, startDateString, dwnFld) -> List[str]:
    """
    Check new files for model. If now new files return empty list

    :return: List of names of new zips with extension (sample [070212021.zip])]
    """

    url = modelParams.DOWNLOAD_URL
    modelDwnFld = os.path.join(dwnFld, modelName)

    newZipNames = check_new_zips(
        url,
        modelDwnFld,
        startDate=datetime.strptime(startDateString, "%Y%m%d")
    )
    current_app.logger.info(f'For {modelName} found new archives {",".join(newZipNames)}')

    if len(newZipNames) == 0:
        current_app.logger.info(f'Not found new archives for model {modelName}')
        return []

    return newZipNames


def download_files(newFiles, modelName, modelParams: ModelParams, dwnFld: os.PathLike):
    for zipName in newFiles:
        modelUrl = modelParams.DOWNLOAD_URL
        download_file_util(modelUrl, zipName, modelName, dwnFld)  # './2021051512.zip'


def extract_files(zipNames, dwnFld, extractFolder):
    # indicatorsForExtract = set()
    # for eventGroup in modelParams.CALCULATIONS:
    #     for eventSubGroup in eventGroup.subgroups:
    #         for conditionGroup in eventSubGroup.condition_groups:
    #             for condition in conditionGroup.conditions:
    #                 indicatorsForExtract.add(condition.index_name)


    for zipName in zipNames:
        archiveDate = zipName.split('.zip')[0]  # 2021051512
        zipPath = os.path.join(dwnFld, zipName)
        destinationFolder = os.path.join(extractFolder, archiveDate)

        # check that folder exists
        if not os.path.exists(extractFolder):
            os.mkdir(extractFolder)

        #extract_rasters(zipPath, extractFolder, indicatorsForExtract)
        extract_rasters(zipPath, destinationFolder, usedIndexes)


def vectorize_rasters(rasterNames: List[str], inRasterFolder, outVectorFolder):
    for rasterName in rasterNames:
        inRasterPath = os.path.join(inRasterFolder, rasterName)

        vectorName = rasterName.replace('tif', 'geojson')

        outVectorPath = os.path.join(outVectorFolder, vectorName)
        polygonize_raster(inRasterPath, outVectorPath, 4326, frmt="GeoJSON")

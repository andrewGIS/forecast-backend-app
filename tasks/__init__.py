import os
import shutil
import time
import urllib
import numpy as np
from osgeo import gdal
from datetime import datetime, timedelta
from config.calculations import calculation_list

from app import celery
from flask import current_app
from processing.utils import (
    check_new_zips,
    download_file_util,
    raster_2_binary,
    extract_rasters,
    merge_file_name,
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

    baseUrl = modelUrls[model]

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
    eventsGroup = calculation_list()

    # generate list of necessary indicators
    indicatorsForExtract = set()
    for eventGroup in eventsGroup:
        for condition in eventGroup["conditions"]:
            indicatorsNames = condition.keys()
            for indicatorName in indicatorsNames:
                indicatorsForExtract.add(indicatorName)

    #models = ['gfs', 'icon']
    models = ['gfs']

    for model in models:
        url = modelUrls[model]
        modelDwnFld = os.path.join(dwnFld, model)
        #newZipNames = check_new_zips(url, modelDwnFld, startDate=datetime(2021, 7, 20))
        newZipNames = ['2021072100.zip']

        if len(newZipNames) == 0:
            # TODO make logging
            pass
            # return

        print(f'For {model} found new archives {",".join(newZipNames)}')

        for zipName in newZipNames:
            archivePath = download_file_util(url, zipName, model)  # './2021051512.zip'
            archiveDate = os.path.basename(archivePath).split('.zip')[0]  # 2021051512
            forecastType = '00' if archiveDate.endswith('00') else '12'
            extractFolder = os.path.join(current_app.config['EXTRACT_FLD'], archiveDate)

            # check that folder exists
            listFolders = [extractFolder]
            for fld in listFolders:
                if not os.path.exists(fld):
                    os.mkdir(fld)

            extract_rasters(archivePath, extractFolder, indicatorsForExtract)

            # delete 027 hour for not intersections three time for forecasting
            hours = ('003', '006', '009', '012', '015', '018', '021', '024')

            for hour in hours:

                for eventGroup in eventsGroup:

                    outName = eventGroup["alias"]
                    eventGroupName = eventGroup["name"]

                    # make true date
                    dateTimeObject = datetime.strptime(archiveDate, '%Y%m%d%H')
                    dateTimeObject = dateTimeObject + timedelta(hours=int(hour))
                    actualDate = dateTimeObject.strftime("%Y%m%d.%H")

                    outRasterPath = os.path.join(
                        outMaskFolder,
                        # f'{model}.{archiveDate}.{hour}.{eventGroupName}.{actualDate}.tif'
                        f'{model}.{forecastType}.{actualDate}.{eventGroupName}.tif'
                    )

                    # conditions for event group
                    conditions = []
                    for condition in eventGroup["conditions"]:
                        masks = []
                        for indicatorName, function in condition.items():
                            rasterName = merge_file_name(model, archiveDate, hour, indicatorName)
                            rasterPath = os.path.join(extractFolder, rasterName)
                            mask = raster_2_binary(rasterPath, function)
                            masks.append(mask)

                        allSubconditions = np.stack(masks, axis=2)
                        # if all separate mask under conditions calculate result mask by min
                        # it mins if one of mask is zero that general condition are also false
                        # and we need to write zero
                        result = np.amin(allSubconditions, axis=2)

                        conditions.append(result)

                    mergedConition = np.stack(conditions, axis=2)
                    # between conditons used or operator (i choose np.any by axis)
                    result = mergedConition.any(axis=2).astype(np.uint8)

                    create_template_raster(outRasterPath)
                    ds = gdal.Open(outRasterPath, gdal.GA_Update)

                    ds.GetRasterBand(1).WriteArray(result)

                    ds = None

            # vectorize
            for rasterName in os.listdir(outMaskFolder):
                inRasterPath = os.path.join(outMaskFolder, rasterName)

                vektorName = rasterName.replace('tif', 'geojson')
                # vektorName = rasterName.replace('tif', 'shp')
                # vektorName =

                outVektor = os.path.join(outVektorFolder, vektorName)
                polygonize_raster(inRasterPath, outVektor, 4326, frmt="GeoJSON")



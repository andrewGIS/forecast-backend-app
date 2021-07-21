from datetime import datetime
import shutil
import urllib
import numpy as np
from flask import current_app
from osgeo import gdal
from osgeo import osr
from osgeo import ogr
import os
import config


def raster_2_binary(rasterPath: str, function) -> np.array:
    """
    Convert first channel of input raster to mask based on
    condition in function
    :param rasterPath: path to input raster
    :param function: function for condition
    :return:
    """
    ds = gdal.Open(rasterPath)
    arr = ds.GetRasterBand(1).ReadAsArray()
    mask = function(arr).astype(np.uint8)
    ds = None

    return mask


def polygonize_raster(inRaster: str, outPath: str, WKID: int, frmt:str="GeoJSON"):


    # map user choose format -> gdal format name
    aviableVectorFormats = {
        "GeoJSON": "GeoJSON",
        "shp": "ESRI Shapefile"
    }
    gdalDriverName = aviableVectorFormats[frmt]

    sourceRaster = gdal.Open(inRaster)
    band = sourceRaster.GetRasterBand(1)

    sr = osr.SpatialReference()
    sr.ImportFromEPSG(WKID)

    driver = ogr.GetDriverByName(gdalDriverName)
    if os.path.exists(outPath):
        driver.DeleteDataSource(outPath)
    outDatasource = driver.CreateDataSource(outPath)
    outLayer = outDatasource.CreateLayer("mask", srs=sr)
    gdal.Polygonize(band, band, outLayer, -1, [], callback=None)
    outDatasource.Destroy()
    sourceRaster = None


def create_template_raster(outPath):
    # Create for target raster the same projection as for the value raster
    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326)
    driver = gdal.GetDriverByName("GTiff")
    dstDs = driver.Create(outPath, config.RASTER_X_SIZE, config.RASTER_Y_SIZE, 1, gdal.GDT_Byte)
    dstDs.SetProjection(outSpatialRef.ExportToWkt())
    dstDs.SetGeoTransform(config.RASTER_GEO_TRANSFORM)


def check_new_zips(url, dwnFld, startDate=datetime(2021, 6, 19)):
    import requests
    from bs4 import BeautifulSoup, SoupStrainer

    response = requests.get(url)
    soup = BeautifulSoup(response.text, parse_only=SoupStrainer('a'), features='html.parser')

    grabbedNames = []
    for link in soup.find_all('a'):
        link = link['href']
        if '.zip' in link:
            grabbedNames.append(link)

    # special filter for checking new archive
    # new archive is archive that is not in dwn folder
    def check_that_zip_new(zipName):
        dnwPath = os.path.join(dwnFld, zipName)
        isExists = os.path.exists(dnwPath)
        if isExists:
            return
        if not startDate:
            return zipName
        if datetime.strptime(zipName, '%Y%m%d%H.zip') >= startDate:
            return zipName
    return list(filter(check_that_zip_new, grabbedNames))


def download_file_util(baseUrl, zipName, model):
    dwnFld = current_app.config['DWN_FLD']

    url = f'{baseUrl}/{zipName}'

    save_path = os.path.join(dwnFld, model)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    save_path_zip = os.path.join(save_path, f'{zipName}')
    with urllib.request.urlopen(url) as response, open(save_path_zip, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
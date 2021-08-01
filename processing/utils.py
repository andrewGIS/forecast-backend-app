from datetime import datetime
import shutil
import urllib
import numpy as np
from zipfile import ZipFile
from flask import current_app
from osgeo import gdal
from osgeo import osr
from osgeo import ogr
import os
from config.settings import Config
import io


def parse_file_name(filename: str, parameter) -> str:
    d = {
        "model": 0,
        "date": 1,
        "hour": 2,
        "indicator": 3,
        "resolution": 4,
    }
    idx = d[parameter]

    return filename.split(".")[idx]


def extract_rasters(inArchive, outPath, indicatorsForExtract):
    with ZipFile(inArchive, 'r') as zipObject:
        listOfFileNames = zipObject.namelist()
        for fileName in listOfFileNames:
            indicator = parse_file_name(fileName, "indicator")
            if indicator in indicatorsForExtract:
                zipObject.extract(fileName, outPath)


def get_index_raster_from_zip(model, date, forecastType, hour, indexName):

    zipFld = Config.DWN_FLD

    # check that model name in existing name
    if model not in Config.MODELS:
        return

    inArchive = os.path.join(zipFld, model, f'{date}{forecastType}.zip')
    out_image = io.BytesIO()
    with ZipFile(inArchive, 'r') as zipObject:
        fileToExtract = f'{model}.{date}{forecastType}.{hour}.{indexName}.tif'
        out_image.write(zipObject.read(fileToExtract))
    out_image.seek(0)
    return out_image


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

    #TODO now polygons is not intersected
    # map user choose format -> gdal format name
    aviableVectorFormats = {
        "GeoJSON": "GeoJSON",
        "shp": "ESRI Shapefile"
    }
    gdalDriverName = aviableVectorFormats[frmt]

    driver = ogr.GetDriverByName(gdalDriverName)
    if os.path.exists(outPath):
        driver.DeleteDataSource(outPath)
    outDataSource = driver.CreateDataSource(outPath)
    newField = ogr.FieldDefn('level_risk', ogr.OFTInteger)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(WKID)
    outLayer = outDataSource.CreateLayer(f"mask", srs=sr)
    outLayer.CreateField(newField)

    # Polygonize
    sourceRaster = gdal.Open(inRaster)
    band = sourceRaster.GetRasterBand(1)
    gdal.Polygonize(band, band, outLayer, 0, [], callback=None)

    outDataSource.Destroy()
    sourceRaster = None


def create_template_raster(outPath, modelName):
    # Create for target raster the same projection as for the value raster
    # output SpatialReference

    # Base geographical data
    # TODO different seeting for different model
    #RASTER_X_SIZE = 161  # base model raster width  #icon 320
    #RASTER_Y_SIZE = 61  # base model raster height  #icon 120
    #RASTER_GEO_TRANSFORM = (34.875, 0.25, 0.0, 65.125, 0.0, -0.25)  # icon (34.9375, 0.125, 0.0, 65.0625, 0.0, -0.125)

    class ModelRasterParams(object):

        def __init__(self, RASTER_X_SIZE, RASTER_Y_SIZE, RASTER_GEO_TRANSFORM):
            self.RASTER_X_SIZE = RASTER_X_SIZE
            self.RASTER_Y_SIZE = RASTER_Y_SIZE
            self.RASTER_GEO_TRANSFORM = RASTER_GEO_TRANSFORM

    #TODO all error in one file
    if modelName not in Config.MODELS:
        raise ValueError("Invalid model name")

    modelsRasterParams = {
        "gfs": ModelRasterParams(
            RASTER_X_SIZE=161,
            RASTER_Y_SIZE=61,
            RASTER_GEO_TRANSFORM=(34.875, 0.25, 0.0, 65.125, 0.0, -0.25)
        ),
        "icon": ModelRasterParams(
            RASTER_X_SIZE=320,
            RASTER_Y_SIZE=120,
            RASTER_GEO_TRANSFORM=(34.9375, 0.125, 0.0, 65.0625, 0.0, -0.125)
        )
    }

    selectedModel: ModelRasterParams = modelsRasterParams[modelName]


    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326)
    driver = gdal.GetDriverByName("GTiff")
    dstDs = driver.Create(outPath, selectedModel.RASTER_X_SIZE, selectedModel.RASTER_Y_SIZE, 1, gdal.GDT_Byte)
    dstDs.SetProjection(outSpatialRef.ExportToWkt())
    dstDs.SetGeoTransform(selectedModel.RASTER_GEO_TRANSFORM)


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
    #TODO check this
    if os.path.exists(save_path_zip):
        return save_path_zip

    with urllib.request.urlopen(url) as response, open(save_path_zip, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    return save_path_zip


def merge_file_name(model, date, hour, indicator) -> str:
    return f'{model}.{date}.{hour}.{indicator}.tif'



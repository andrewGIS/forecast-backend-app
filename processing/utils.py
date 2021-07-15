import numpy as np
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
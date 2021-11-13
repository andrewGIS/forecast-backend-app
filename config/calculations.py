from models.forecast_models import CalcGroup

import os
from abc import ABC
from osgeo import gdal
import numpy as np


class Variable(np.lib.mixins.NDArrayOperatorsMixin, ABC):

    def __init__(self, rasterPrefix, indexName):
        self.rasterPrefix = rasterPrefix
        self.indexName = indexName

    def __array__(self):
        ds = gdal.Open(f"{self.rasterPrefix}.{self.indexName}.tif")
        arr = ds.GetRasterBand(1).ReadAsArray()
        ds = None
        return arr


def path_decorator(model='gfs'):
    def actual_decorator(func):
        def wrapper(tifFolder, date, forecastHour):
            prefix = os.path.join(tifFolder, f'{model}.{date}.0{forecastHour}')
            return func(prefix)
        return wrapper
    return actual_decorator


@path_decorator(model='gfs')
def squall_gfs(rasterPrefix) -> np.array:
    """

    :param tifFolder: Распакованные растры
    :param date: Исходная дата
    :param forecastHour: Час для расчета
    :param model modelName модель для расчета
    :return:
    """

    #rasterPrefix = os.path.join(tifFolder, f'{model}.{date}.0{forecastHour}')

    cape_surface = Variable(rasterPrefix, indexName="cape_surface")
    cape_255 = Variable(rasterPrefix, indexName="cape_255-0")
    dls = Variable(rasterPrefix, indexName="dls")
    wmaxshear = Variable(rasterPrefix, indexName="wmaxshear")

    Level1 = ((cape_surface > 1500) & (cape_255 > 200) & (dls > 26) & (wmaxshear > 1100)).astype(np.uint8)
    Level1 = np.where(Level1 == 0, 0, 1)

    Level2 = ((cape_surface > 1000) & (cape_255 > 1500) & (dls > 21) & (wmaxshear > 850)).astype(np.uint8)
    Level2 = np.where(Level2 == 0, 0, 2)

    Level3 = (
            ((cape_surface > 600) & (cape_255 > 1000) & (dls > 18) & (wmaxshear > 600)) |
            ((cape_surface > 1500) & (cape_255 > 2000) & (dls > 15) & (wmaxshear > 500))
    ).astype(np.uint8)
    Level3 = np.where(Level3 == 0, 0, 3)

    Level4 = (
            ((cape_surface > 400) & (cape_255 > 700) & (dls > 15) & (wmaxshear > 500)) |
            ((cape_surface > 1500) & (cape_255 > 2000)) |
            ((cape_surface > 200) & (cape_255 > 400) & (dls > 21))
    )
    Level4 = np.where(Level4 == 0, 0, 4)

    # select most danger group for each pixel
    result = np.stack([Level1, Level2, Level3, Level4], axis=2)
    # need mask for zero values
    result = np.ma.masked_equal(result, 0.0)
    result = result.min(axis=2)
    result = result.filled(fill_value=0)

    return result


@path_decorator(model='icon')
def squall_icon(rasterPrefix) -> np.array:
    """

    :param tifFolder: Распакованные растры
    :param date: Исходная дата
    :param forecastHour: Час для расчета
    :param model modelName модель для расчета
    :return:
    """

    #rasterPrefix = os.path.join(tifFolder, f'{model}.{date}.0{forecastHour}')

    dls = Variable(rasterPrefix, indexName="dls")

    Level1 = (dls > 1500).astype(np.uint8)
    Level1 = np.where(Level1 == 0, 0, 1)

    # select most danger group for each pixel
    result = np.stack([Level1], axis=2)
    # need mask for zero values
    result = np.ma.masked_equal(result, 0.0)
    result = result.min(axis=2)
    result = result.filled(fill_value=0)

    return result


'''
TODO manual is it possibible automate
used index dict
'''
usedIndexes = ["cape_surface", "cape_255-0", "dls", "wmaxshear"]


# gfs calculations
SQUALL_GFS: CalcGroup = CalcGroup(
    alias="Шквалы",
    name="squall",
    calculation=squall_gfs
)

# icon calculations
SQUALL_ICON: CalcGroup = CalcGroup(
    alias="Шквалы",
    name="squall",
    calculation=squall_icon
)

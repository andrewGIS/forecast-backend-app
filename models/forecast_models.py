from typing import List, Callable


class CalcGroup(object):
    """
    General class for group of event e.g. squalls
    """

    def __init__(self, alias, name, calculation: Callable):
        self.alias = alias  # Шквалы
        self.name = name  # squall
        self.calculation = calculation


class ModelParams(object):

    def __init__(self,
                 RASTER_X_SIZE,
                 RASTER_Y_SIZE,
                 RASTER_GEO_TRANSFORM,
                 DOWNLOAD_URL,
                 CALCULATIONS: List[CalcGroup],
                 INDEXES: List[str]
                 ):
        self.RASTER_X_SIZE = RASTER_X_SIZE
        self.RASTER_Y_SIZE = RASTER_Y_SIZE
        self.RASTER_GEO_TRANSFORM = RASTER_GEO_TRANSFORM
        self.DOWNLOAD_URL = DOWNLOAD_URL
        self.CALCULATIONS = CALCULATIONS
        self.INDEXES = INDEXES

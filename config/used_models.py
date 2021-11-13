"""
Файл используется для описания конкретных моделей в проекте
"""
# RASTER_X_SIZE = 161  # base model raster width  #icon 320
# RASTER_Y_SIZE = 61  # base model raster height  #icon 120
# RASTER_GEO_TRANSFORM = (34.875, 0.25, 0.0, 65.125, 0.0, -0.25)  # icon (34.9375, 0.125, 0.0, 65.0625, 0.0, -0.125)
# modelUrls = {
#     "icon": "http://84.201.155.104/icon-ural/",
#     "gfs": "http://84.201.155.104/gfs-ural/",
# }
from models.forecast_models import ModelParams
from .calculations import SQUALL_ICON, SQUALL_GFS


models = {
    "gfs": ModelParams(
        RASTER_X_SIZE=161,
        RASTER_Y_SIZE=61,
        RASTER_GEO_TRANSFORM=(34.875, 0.25, 0.0, 65.125, 0.0, -0.25),
        DOWNLOAD_URL="http://84.201.155.104/gfs-ural/",
        CALCULATIONS=[SQUALL_GFS],
        INDEXES=[
            'cape_180-0', 'cape_255-0', 'cape_surface', 'cin_180-0', 'cin_255-0',
            'cin_surface', 'dls', 'dpt_2m', 'ehi', 'hlcy', 'k', 'lls', 'mls',
            'prate_surface', 'pwat', 'rh_900', 'tmp_2m', 'tmp_850', 'tmp_900',
            'tmp_925', 'tt', 'wmaxshear', 'ws_10m'
        ]

    ),
    "icon": ModelParams(
        RASTER_X_SIZE=320,
        RASTER_Y_SIZE=120,
        RASTER_GEO_TRANSFORM=(34.9375, 0.125, 0.0, 65.0625, 0.0, -0.125),
        DOWNLOAD_URL="http://84.201.155.104/icon-ural/",
        CALCULATIONS=[SQUALL_ICON],
        INDEXES=[
            'cape_con', 'dls', 'htop_con', 'k', 'lls', 'mls', 'pmsl', 't_2m',
            'td_2m', 'tot_prec', 'tt', 'vmax_10m', 'ws_10m', 'ww'
        ]
    )
}

MODELS = list(models.keys())


def event_group_list(modelName):
    result = []
    selectedModel = models[modelName]
    for group in selectedModel.CALCULATIONS:
        result.append({group.name: group.alias})
    return result

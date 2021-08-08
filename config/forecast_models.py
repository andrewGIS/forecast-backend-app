# RASTER_X_SIZE = 161  # base model raster width  #icon 320
# RASTER_Y_SIZE = 61  # base model raster height  #icon 120
# RASTER_GEO_TRANSFORM = (34.875, 0.25, 0.0, 65.125, 0.0, -0.25)  # icon (34.9375, 0.125, 0.0, 65.0625, 0.0, -0.125)
# modelUrls = {
#     "icon": "http://84.201.155.104/icon-ural/",
#     "gfs": "http://84.201.155.104/gfs-ural/",
# }
from .models import ModelParams
from .calculations import SQUALL_ICON, SQUALL_GFS


models = {
    "gfs": ModelParams(
        RASTER_X_SIZE=161,
        RASTER_Y_SIZE=61,
        RASTER_GEO_TRANSFORM=(34.875, 0.25, 0.0, 65.125, 0.0, -0.25),
        DOWNLOAD_URL="http://84.201.155.104/gfs-ural/",
        CALCULATIONS=[SQUALL_GFS]
    ),
    "icon": ModelParams(
        RASTER_X_SIZE=320,
        RASTER_Y_SIZE=120,
        RASTER_GEO_TRANSFORM=(34.9375, 0.125, 0.0, 65.0625, 0.0, -0.125),
        DOWNLOAD_URL="http://84.201.155.104/icon-ural/",
        CALCULATIONS=[SQUALL_ICON]
    )
}

MODELS = list(models.keys())


def event_group_list(modelName):
    result = []
    selectedModel = models[modelName]
    for group in selectedModel.CALCULATIONS:
        result.append({group.name: group.alias})
    return result

import os

class BaseConfig():
    TESTING = False
    RASTER_X_SIZE = 161  # base model raster width
    RASTER_Y_SIZE = 61  # base model raster height
    RASTER_GEO_TRANSFORM = (34.875, 0.25, 0.0, 65.125, 0.0, -0.25)
    VECTOR_FLD = os.path.normpath('./data/vector')
    DOWNLOAD_FLD = os.path.normpath('./data/download')
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


class DevConfig(BaseConfig):
    FLASK_ENV = 'development'
    DEBUG = True


class ProdConfig(BaseConfig):
    FLASK_ENV = 'production'


class TestConfig(BaseConfig):
    FLASK_ENV = 'development'
    TESTING = True
    DEBUG = True
    # make celery execute tasks synchronously in the same process
    CELERY_ALWAYS_EAGER = True
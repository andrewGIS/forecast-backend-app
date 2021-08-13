import os
from dotenv import load_dotenv

load_dotenv()

# Find the absolute file path to the top level project directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class. Contains default configuration settings +
    configuration settings applicable to all environments.
    """
    # Default settings

    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    # delete 027 hour for not intersections three time for forecasting
    # all hours are
    # ('003', '006', '009', '012', '015', '018', '021', '024', '027')
    PROCESSING_HOURS = ('03', '06', '09', '12', '15', '18', '21', '24')

    # Folders
    VECTOR_FLD = os.path.normpath('./data/vector')
    EXTRACT_FLD = os.path.normpath('./data/extract')
    # TODO rename mask folder
    MASK_FLD = os.path.normpath('./data/masks')
    DWN_FLD = os.path.normpath('./data/download')

    # Settings applicable to all environments
    FLASK_ENV = os.getenv('SECRET_KEY', default='development')
    SECRET_KEY = os.getenv('SECRET_KEY', default='A very terrible secret key.')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    RESULT_BACKEND = os.getenv('RESULT_BACKEND')
    FIRST_ZIP_DATE = os.getenv("FIRST_ZIP_DATE")  # in YYYYmmdd format


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    HOST = 'localhost:5000'


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    FIRST_ZIP_DATE = "20210811"
    #SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'test.db')


class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    HOST = "ogs.psu.ru:5001"
    #FIRST_ZIP_DATE = "20210809"
    #SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DATABASE_URI', default="sqlite:///" + os.path.join(basedir, 'prod.db'))
# TODO rewrite all with RestPlus library
import os

from config.settings import Config

from flask import Flask
from flask_cors import CORS
from celery import Celery

### Instantiate Celery ###
celery = Celery(
    __name__,
    broker=Config.CELERY_BROKER_URL,
    result_backend=Config.RESULT_BACKEND
)

def create_app():

    app = Flask(__name__)

    CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.setting.DevelopmentConfig')

    app.config.from_object(CONFIG_TYPE)

    # CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*"
        }
    })

    # Configure celery
    celery.conf.update(app.config)

    register_blueprints(app)

    return app


def register_blueprints(app: Flask):
    from api.v1.forecast import api as forecast_api
    from api.v1.configs import api as config_api
    app.register_blueprint(forecast_api, url_prefix="/api/v1")
    app.register_blueprint(config_api, url_prefix="/api/v1")

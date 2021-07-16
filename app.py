import logging
import config

from flask import Flask
from flask_cors import CORS

from api.forecast import api as forecast_api
from api.configs import api as config_api

logger = logging.getLogger()


def create_app():

    logger.info(f'Starting app in {config.APP_ENV} environment')

    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {
            "origins": "*"
        }
    })


    app.config.from_object('config')

    app.register_blueprint(forecast_api)
    app.register_blueprint(config_api)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)



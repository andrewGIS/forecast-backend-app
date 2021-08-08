from flask import (
    Blueprint,
    jsonify,
    request
)

from config.forecast_models import MODELS, models
from config.models import ModelParams

api = Blueprint('configs', __name__)


@api.route('/models', methods=['GET'])
def get_available_models():
    """Endpoint returning a list of forecast models names.
    ---
    definitions:
      Models:
        type: object
        properties:
          models:
            type: array
            items:
              $ref: '#/definitions/ModelName'
      ModelName:
        type: string
    responses:
      200:
        description: A list of available models name
        schema:
          $ref: '#/definitions/ModelName'
    """
    return jsonify({"models": MODELS}), 200


@api.route('/event_groups', methods=['GET'])
def get_available_groups():
    # TODO status ok with class
    modelName = request.args.get('model_name')
    selectedModel: ModelParams = models[modelName]
    groupsList = [{"name": group.name, "alias": group.alias} for group in selectedModel.CALCULATIONS]
    return jsonify({"groups": groupsList}), 200

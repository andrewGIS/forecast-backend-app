from flask import (
    Blueprint,
    jsonify,
    request
)

from config.used_models import MODELS, models
from models.forecast_models import ModelParams

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
    """Endpoint returning a list of subgroup for model.
    ---
    parameters:
    - name: model
      in: query
      type: string
      enum: ['gfs', 'icon']
      required: true
      default: 'gfs'
    definitions:
      Groups:
        type: object
        properties:
          groups:
            type: array
            items:
              $ref: '#/definitions/Group'
      Group:
        type: object
        properties:
            name:
              type: string
            alias:
              type: string
    responses:
      200:
        description: A list of available group for model
    """
    # TODO status ok with class
    modelName = request.args.get('model')
    selectedModel: ModelParams = models[modelName]
    groupsList = [{"name": group.name, "alias": group.alias} for group in selectedModel.CALCULATIONS]
    return jsonify({"groups": groupsList}), 200


@api.route('/indexes', methods=['GET'])
def get_available_indexes():
    """Endpoint returning a list of available indexes for model
        ---
        parameters:
        - name: model
          in: query
          type: string
          enum: ['gfs', 'icon']
          required: true
          default: 'gfs'
        definitions:
          Indexes:
            type: object
            properties:
              indexes:
                type: array
                items:
                  $ref: '#/definitions/Index'
          Index:
            type: string
        responses:
          200:
            description: A list of available indexes for model
    """
    modelName = request.args.get('model')
    selectedModel: ModelParams = models[modelName]
    return jsonify({"indexes": selectedModel.INDEXES}), 200

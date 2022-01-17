import os
from datetime import datetime

from flask import (
    Blueprint,
    request,
    json,
    jsonify,
    current_app, send_file
)
from werkzeug import exceptions

from models.forecast_models import ModelParams, CalcGroup
from tasks.process_forecast import celery, process_new_files
from tasks.process_forecast import create_task, download_file
from processing.utils import get_index_raster_from_zip
from config.used_models import MODELS, models
from processing.utils import get_index_rasters_by_date, available_dates

api = Blueprint('forecast', __name__)


@api.route('/get_forecast', methods=['GET'])
def get_forecast():
    """Endpoint is used for get forecast raster or vector layer (GeoJSON)
    It contains polygons with different code level of danger
    1 - high risk event
    ...
    4 - minimum risk event
    Count of level may be different
    This is using docstrings for specifications.
        ---
        parameters:
          - name: model
            in: query
            type: string
            enum: ['gfs', 'icon']
            required: true
            default: 'gfs'
          - name: date
            description: Дата в формате YYYYmmdd UTC, на который необходим прогноз
            in: query
            type: string
            required: true
            default: None
          - name: hour
            description: Час для которого запрашивает прогноз (UTC)
            enum: ['03', '06', '09', '12', '15', '18', '21', '24']
            in: query
            type: string
            required: true
            default: '03'
          - name: group
            description: Группа явлений, для которых запрашивается прогноз (например, squall - шквалы).
            in: query
            type: string
            required: true
            default: None
          - name: datatype
            description: Формат данных
            in: query
            type: string
            enum: ['vector', 'raster']
            required: true
            default: 'vector'
        definitions:
          GeoJSON:
            type: object
          Error:
            type: object
            properties:
              error:
                type: string
        responses:
          200:
            description: GeoJSON object with forecast
          400:
            description: Errors when some parameters are invalid
            schema:
              $ref: '#/definitions/Error'
        """
    modelName = request.args.get('model', None)  # use default value replace 'None'
    date = request.args.get('date', None)
    hour = request.args.get('hour', None)
    group = request.args.get('group', None)
    dataType = request.args.get('datatype', None)

    if not all([modelName, date, hour, group]):
        return jsonify(error="Not all params specified"), exceptions.BadRequest.code

    if modelName not in MODELS:
        return jsonify(
            error=f"Unknown model, known models are {','.join(MODELS)}"
        ), exceptions.BadRequest.code

    try:
        datetime.strptime(date, '%Y%m%d')
    except ValueError:
        return jsonify(
            error=f"Error in parsing date get, except date in format YYYYmmdd"
        ), exceptions.BadRequest.code

    availableHours = current_app.config['PROCESSING_HOURS']
    if hour not in availableHours:
        return jsonify(
            error=f"Unknown hour, known hour are {','.join(availableHours)}"
        ), exceptions.BadRequest.code

    selectedModel: ModelParams = models[modelName]
    groupsList = [group.name for group in selectedModel.CALCULATIONS]
    if group not in groupsList:
        return jsonify(
            error=f"Unknown group for model {modelName}, known hour are {','.join(groupsList)}"
        ), exceptions.BadRequest.code

    if dataType not in ['vector', 'raster']:
        return jsonify(
            error=f"Unknown data format known hour are vector, raster"
        ), exceptions.BadRequest.code

    # проверяем есть ли вектор (или растр) с прогнозом на эту дату (пытаемся взять прогноз и от 00 и от 12
    # как только нашли - отдаем, сначала проверяем более поздний срок (от 12 часов), потом от 00 часов
    fld = current_app.config['VECTOR_FLD'] if dataType == 'vector' else current_app.config['MASK_FLD']
    extension = 'geojson' if dataType == 'vector' else 'tif'

    forecastTypes = ["12", "00"]
    for forecastType in forecastTypes:
        fileToSend = os.path.join(fld, f'{modelName}.{forecastType}.{date}.{hour}.{group}.{extension}')

        if os.path.exists(fileToSend):

            if dataType == 'vector':
                with open(fileToSend) as f:
                    data = json.load(f)
                return data

            if dataType == 'raster':
                return send_file(
                    fileToSend,
                    mimetype="image/tif",
                    download_name=f'{modelName}.{forecastType}.{date}.{hour}.{group}.tif'
                )
            break

    return jsonify(error="No json for specific date"), exceptions.BadRequest.code


@api.route('/test_task/', methods=['GET'])
def run_task():
    task_type = request.args.get('type')
    task = create_task.delay(int(task_type))
    return jsonify({"task_id": task.id}), 202


@api.route('/download/')
def run_download():
    name = request.args.get('zipname')
    model = request.args.get('model')
    task = download_file.delay(name, model)
    return jsonify({"task_id": task.id}), 200


@api.route('/processing_debug/')
def run_processing():
    # TODO handler error
    #process_new_files()
    #process_new_files_v2()
    process_new_files()
    return jsonify('ok'), 200


@api.route('/tasks/<task_id>', methods=["GET"])
def get_status(task_id):
    task_result = celery.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        # "task_result": task_result.result
    }
    return jsonify(result), 200


@api.route('/get_index', methods=["GET"])
def get_index():
    """Endpoint is used for get init raster value
    ---
    parameters:
      - name: model
        in: query
        type: string
        enum: ['gfs', 'icon']
        required: true
        default: 'gfs'
      - name: date
        description: Дата в формате YYYYmmdd UTC, для которой нужен растр
        in: query
        type: string
        required: true
        default: None
      - name: forecast_type
        description: Тип прогноза 00 - от полночи, 12 - от полудня
        in: query
        type: string
        enum: ['00', '12']
        required: true
        default: '00'
      - name: hour
        description: Час для которого запрашивает прогноз (UTC)
        enum: ['03', '06', '09', '12', '15', '18', '21', '24']
        in: query
        type: string
        required: true
        default: '03'
      - name: index_name
        description: Название индекса
        in: query
        type: string
        required: true
        default: None
    definitions:
      GeoJSON:
        type: object
      Error:
        type: object
        properties:
          error:
            type: string
    responses:
      200:
        description: Result raster as byte IO Stream
      400:
        description: Errors when some parameters are invalid
        schema:
          $ref: '#/definitions/Error'
    """
    model = request.args.get('model')
    date = request.args.get('date')
    forecastType = request.args.get('forecast_type')
    hour = request.args.get('hour')
    indexName = request.args.get('index_name')

    if not all([model, date, forecastType, hour, indexName]):
        return "Not all params specified"

    file = get_index_raster_from_zip(model, date, forecastType, hour, indexName)
    return send_file(
        file,
        mimetype="image/tif",
        download_name=f'{model}.{date}{forecastType}.{hour}.{indexName}.tif'
    )


@api.route('/get_legend', methods=['GET'])
def get_legend():
    """Endpoint is used for get legend for specific group
    ---
    parameters:
      - name: model
        in: query
        type: string
        enum: ['gfs', 'icon']
        required: true
        default: 'gfs'
      - name: group
        description: Группа явлений, для которых запрашивается прогноз (например, squall - шквалы).
        in: query
        type: string
        required: true
        default: 'squall'
    definitions:
      Legend:
        type: object
        properties:
          legend:
            type: array
            items:
              $ref: '#/definitions/LegendItem'
      LegendItem:
        type: object
        properties:
          levelCode:
            type: number
          name:
            type: string
          alias:
            type: string
    responses:
      200:
        description: Legend for specific group
        schema:
          $ref: '#/definitions/Legend'
    """
    # TODO check why not working ref in response
    model = request.args.get('model')
    groupName = request.args.get('group')

    selectedModel = models[model]

    selectedGroup: CalcGroup = next(filter(lambda x: x.name == groupName, selectedModel.CALCULATIONS))

    serialized_object = [
        {
            "levelcode": subevent.level_code,
            "name": subevent.name,
            "alias": subevent.alias
        }
        for subevent in selectedGroup.subgroups
    ]

@api.route('/get_dates', methods=['GET'])
def get_dates():
    """Aviable dates for forecasting
    ---
    parameters:
      - name: model
        in: query
        type: string
        enum: ['gfs', 'icon']
        required: true
        default: 'gfs'
    definitions:
      Dates:
        type: object
        properties:
          legend:
            type: array
            items:
              $ref: '#/definitions/DateStr'
      DateStr:
        type: string
    responses:
      200:
        description: Avialable dates
        schema:
          $ref: '#/definitions/Dates'
    """
    model = request.args.get('model')
    vector_folder = current_app.config['VECTOR_FLD']

    return jsonify(available_dates(model, vector_folder))

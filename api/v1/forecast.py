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

from config.models import ModelParams
from tasks.process_forecast import celery
from tasks.process_forecast import create_task, download_file, process_new_files
from processing.utils import get_index_raster_from_zip
from config.forecast_models import MODELS, models


api = Blueprint('forecast', __name__)


@api.route('/get_forecast/', methods=['GET'])
def get_forecast():
    modelName = request.args.get('model', None)  # use default value replace 'None'
    forecastType = request.args.get('forecast_type', None)  # use default value replace 'None'
    date = request.args.get('date', None)
    hour = request.args.get('hour', None)
    group = request.args.get('group', None)

    if not all([modelName, forecastType, date, hour, group]):
        return jsonify(error="Not all params specified"), exceptions.BadRequest.code

    if modelName not in MODELS:
        return jsonify(
            error=f"Unknown model, known models are {','.join(MODELS)}"
        ), exceptions.BadRequest.code

    # TODO move to config
    forecastTypes = ["00", "12"]
    if forecastType not in forecastTypes:
        return jsonify(
            error=f"Unknown model, known forestTypes are {','.join(forecastTypes)}"
        ), exceptions.BadRequest.code

    try:
        dateTimeObject = datetime.strptime(date, '%Y%m%d')
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

    vectorFolder = current_app.config['VECTOR_FLD']
    fileToSend = os.path.join(vectorFolder, f'{modelName}.{forecastType}.{date}.{hour}.{group}.geojson')

    if not os.path.exists(fileToSend):
        return jsonify(error="No json for specific date"), exceptions.BadRequest.code

    with open(fileToSend) as f:
        data = json.load(f)
    return data


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
    process_new_files()
    return jsonify('ok'), 200


@api.route('/tasks/<task_id>', methods=["GET"])
def get_status(task_id):
    task_result = celery.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        #"task_result": task_result.result
    }
    return jsonify(result), 200


@api.route('/get_index/', methods=["GET"])
def get_index():
    model = request.args.get('model')
    date = request.args.get('date')
    forecastType = request.args.get('forecastType')
    hour = request.args.get('hour')
    indexName = request.args.get('indexName')

    if not all([model, date, forecastType, hour, indexName]):
        return "Not all params specified"

    file = get_index_raster_from_zip(model, date, forecastType, hour, indexName)
    return send_file(
        file,
        mimetype="image/tif",
        download_name=f'{model}.{date}{forecastType}.{hour}.{indexName}.tif'
    )

import os

from celery.result import AsyncResult

from tasks import celery

import config

from flask import (
    Blueprint,
    request,
    json, jsonify
)

from tasks import create_task, download_file

api = Blueprint('forecast', __name__)

vectorFolder = config.VECTOR_FLD


@api.route('/get_forecast/', methods=['GET'])
def make_predict():
    model = request.args.get('model', None)  # use default value repalce 'None'
    forecastType = request.args.get('forecast_type', None)  # use default value repalce 'None'
    date = request.args.get('date', None)
    hour = request.args.get('hour', None)
    group = request.args.get('group', None)

    if not all([model,forecastType, date, hour, group]):
        return "Not all params specified"

    fileToSend = os.path.join(vectorFolder,f'{model}.{forecastType}.{date}.{hour}.{group}.geojson')
    # cloud filtered data

    if not os.path.exists(fileToSend):
        return "No forecast for specific date"

    with open(fileToSend) as f:
        data = json.load(f)
    return data


@api.route('/test_task/', methods=['GET'])
def run_task():
    task_type = request.args.get('type')
    task = create_task.delay(int(task_type))
    return jsonify({"task_id": task.id}), 202


@api.route('/download/')
def run_donwload():
    name = request.args.get('zipname')
    model = request.args.get('model')
    task = download_file.delay(name, model)
    return jsonify({"task_id": task.id}), 202

@api.route('/tasks/<task_id>', methods=["GET"])
def get_status(task_id):
    task_result = celery.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        #"task_result": task_result.result
    }
    return jsonify(result), 200

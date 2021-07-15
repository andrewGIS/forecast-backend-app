import os
import config

from flask import (
    Blueprint,
    request,
    json
)
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
    with open(fileToSend) as f:
        data = json.load(f)
    return data

from flask import (
    Blueprint,
    jsonify,
    abort
)
from config import calculations
import werkzeug.exceptions

api = Blueprint('configs', __name__)


@api.route('/event_groups', methods=['GET'])
def get_available_groups():
    groups = calculations.event_group_list()
    return jsonify(groups)


@api.route('/models', methods=['GET'])
def get_available_models():
    return jsonify(error="Not implemented"), werkzeug.exceptions.NotImplemented.code

from flask import (
    Blueprint,
    jsonify
)
from config import calculations

api = Blueprint('configs', __name__)


@api.route('/event_groups', methods=['GET'])
def get_avaliable_groups():
    groups = calculations.event_group_list()
    return jsonify(groups)


@api.route('/models', methods=['GET'])
def get_aviable_models():
    return NotImplementedError

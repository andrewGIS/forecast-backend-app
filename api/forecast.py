from flask import Blueprint

api = Blueprint('cloud', __name__)


@api.route('/makecloudmask/<foldername>', methods=['GET'])
def run_process(foldername):
    return "ok"
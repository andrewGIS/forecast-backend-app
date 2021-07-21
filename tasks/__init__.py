import os
import shutil
import time
import urllib

from app import celery
from flask import current_app


@celery.task(name="app.tasks.create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


@celery.task(name="app.tasks.download_file")
def download_file(zipName, model):
    dwnFld = current_app.config['DWN_FLD']

    modelUrls = {
        "icon": "http://84.201.155.104/icon-ural/",
        "gfs": "http://84.201.155.104/gfs-ural/",
    }

    baseUrl = modelUrls[model]

    url = f'{baseUrl}/{zipName}.zip'

    save_path = os.path.join(dwnFld, model)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    save_path_zip = os.path.join(save_path, f'{zipName}.zip')
    with urllib.request.urlopen(url) as response, open(save_path_zip, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

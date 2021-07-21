import os
import shutil
import time
import urllib
from datetime import datetime

from app import celery
from flask import current_app
from processing.utils import check_new_zips, download_file_util

modelUrls = {
    "icon": "http://84.201.155.104/icon-ural/",
    "gfs": "http://84.201.155.104/gfs-ural/",
}


@celery.task(name="app.tasks.create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


# saved as sample celery task
@celery.task(name="app.tasks.download_file")
def download_file(zipName, model):
    dwnFld = current_app.config['DWN_FLD']

    baseUrl = modelUrls[model]

    url = f'{baseUrl}/{zipName}.zip'

    save_path = os.path.join(dwnFld, model)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    save_path_zip = os.path.join(save_path, f'{zipName}.zip')
    with urllib.request.urlopen(url) as response, open(save_path_zip, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

@celery.task(name="app.tasks.check_new_files")
def process_new_files():
    dwnFld = current_app.config['DWN_FLD']

    for model in ['gfs', 'icon']:
        url = modelUrls[model]
        modelDwnFld = os.path.join(dwnFld, model)
        newZipNames = check_new_zips(url, modelDwnFld, startDate=datetime(2021, 7, 19))

        if len(newZipNames) == 0:
            # TODO make logging
            return

        print(newZipNames)

        for zipName in newZipNames:
            download_file_util(url, zipName, model)


import time

from celery import Celery

# import config
from flask import jsonify

celery = Celery(__name__)
# celery.conf.broker_url = config.CELERY_BROKER_URL
# celery.conf.result_backend = config.CELERY_RESULT_BACKEND

celery.conf.broker_url = 'redis://localhost:6379'
celery.conf.result_backend = 'redis://localhost:6379'
#celery.conf.backend = 'redis://localhost:6379'

# celery = Celery(
#         app.import_name,
#         broker=config.CELERY_BROKER_URL,
#         backend=config.CELERY_RESULT_BACKEND
# )

    # celery.conf.update(app.config)
    #
    # class ContextTask(celery.Task):
    #     def __call__(self, *args, **kwargs):
    #         with app.app_context():
    #             return self.run(*args, **kwargs)
    #
    # celery.Task = ContextTask
    #
    # return celery


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True




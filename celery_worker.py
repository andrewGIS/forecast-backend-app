from app import create_app

app = create_app()
app.app_context().push()

from app import celery

# sample run task with args
# celery.conf.beat_schedule = {
#     'downloadnewfile': {
#         'task': 'app.tasks.download_file',
#         'schedule': 60.0,
#         'args': ('2021072000', 'gfs')
#     }
# }
celery.conf.beat_schedule = {
    'check-zips-on-server': {
        'task': 'app.tasks.check_new_files',
        'schedule': 60.0
    }
}
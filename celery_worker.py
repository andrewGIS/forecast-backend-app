from celery.schedules import crontab
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

# TODO move switching in Env
# dev conf
# celery.conf.beat_schedule = {
#     'check-zips-on-server': {
#         'task': 'app.tasks.check_new_files',
#         'schedule': 60.0
#     }
# }

# prod conf date in UTC
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=2, minute=50),
        app.tasks.check_new_files(),
    )
    sender.add_periodic_task(
        crontab(hour=4, minute=30),
        app.tasks.check_new_files(),
    )
    sender.add_periodic_task(
        crontab(hour=14, minute=50),
        app.tasks.check_new_files(),
    )
    sender.add_periodic_task(
        crontab(hour=15, minute=30),
        app.tasks.check_new_files(),
    )

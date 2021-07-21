from app import create_app

app = create_app()
app.app_context().push()

from app import celery

celery.conf.beat_schedule = {
    'check-zips-on-server': {
        'task': 'app.tasks.download_file',
        'schedule': 60.0,
        'args': ('2021072000', 'gfs')
    }
}
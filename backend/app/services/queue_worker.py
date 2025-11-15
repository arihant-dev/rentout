from celery import Celery # type: ignore

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def process_task(data):
    # heavy ML compute here
    return "done"

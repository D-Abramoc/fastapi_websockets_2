import asyncio
import time

from celery import Celery

from bot.main import bot

# import tracemalloc

# tracemalloc.start()


celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)


@celery_app.task
def send_notification(client_id: int, message: str):
    try:
        asyncio.get_event_loop().run_until_complete(
            bot.send_message(client_id, message)
        )
    except Exception:
        pass
    # await bot.send_message(client_id, message)
    return 'ok'


# import os
# import time

# from celery import Celery


# celery = Celery(__name__)
# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


# @celery.task(name="create_task")
# def create_task(task_type):
#     time.sleep(int(task_type) * 10)
#     return True

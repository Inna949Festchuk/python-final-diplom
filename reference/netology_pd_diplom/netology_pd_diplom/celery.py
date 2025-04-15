# по материалам 
# https://realpython.com/asynchronous-tasks-with-django-and-celery/
# https://stackabuse.com/asynchronous-tasks-in-django-with-redis-and-celery/

import os
from celery import Celery
from celery.result import AsyncResult

# Устанавливаем модуль настроек Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netology_pd_diplom.settings')

# Создаем экземпляр Celery
app = Celery('netology_pd_diplom')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач (tasks.py в каждом приложении)
app.autodiscover_tasks()

def get_result(task_id: str) -> AsyncResult:
    """
    Функция для получения результата асинхронной задачи
    :param task_id: Идентификатор задачи
    :return: Объект AsyncResult
    """
    return AsyncResult(task_id, app=app)
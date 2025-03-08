from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        """
        импортируем сигналы
        """
        # import backend.signals  # Импорт сигналов при старте приложения
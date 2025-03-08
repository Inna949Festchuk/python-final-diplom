from django.apps import AppConfig

class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        # Импортируем обработчики сигналов здесь, чтобы избежать циклических импортов
        from backend.signals import (
            password_reset_token_created, 
            new_user_registered_signal, 
            new_order_signal
        )
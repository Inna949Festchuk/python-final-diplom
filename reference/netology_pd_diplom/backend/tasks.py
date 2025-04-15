from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from backend.models import ConfirmEmailToken, User, Order


@shared_task
def send_password_reset_email(reset_password_token_key: str, user_email: str):
    """
    Асинхронная задача для отправки email с токеном сброса пароля.

    Args:
        reset_password_token_key (str): Токен для сброса пароля.
        user_email (str): Email пользователя.
    """
    msg = EmailMultiAlternatives(
        # Заголовок
        f"Восстановление пароля",
        # Тело сообщения
        reset_password_token_key,
        # Отправитель
        settings.EMAIL_HOST_USER,
        # Получатель
        [user_email],
    )
    msg.send()


@shared_task
def send_new_user_confirmation_email(token: str, email: str):
    """
    Асинхронная задача для отправки email с подтверждением регистрации.

    Args:
        token (str): Токен для подтверждения email.
        email (str): Email пользователя.
    """
    msg = EmailMultiAlternatives(
        # Заголовок
        "Подтверждение регистрации ",
        # Тело сообщения
        f"Ваш токен для подтверждения email: {token}",
        # Отправитель
        settings.EMAIL_HOST_USER,
        # Получатель
        [email],
    )
    msg.send()


@shared_task
def send_order_status_update_email(user_email: str, order_id: int, state_display: str):
    """
    Асинхронная задача для отправки уведомления о смене статуса заказа.

    Args:
        user_email (str): Email пользователя.
        order_id (int): ID заказа.
        state_display (str): Человеко-читаемый статус заказа.
    """
    msg = EmailMultiAlternatives(
        # Заголовок
        f"Обновление статуса заказа №{order_id}",
        # Сообщение с текущим статусом
        f"Статус вашего заказа изменен на: {state_display}",
        # Отправитель
        settings.EMAIL_HOST_USER,
        # Получатель
        [user_email],
    )
    msg.send()

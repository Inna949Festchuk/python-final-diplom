from typing import Type

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User, Order

# Сигналы для отслеживания событий, таких как создание нового 
# пользователя и сброс пароля. Каждый раз, когда происходит событие, соответствующий 
# обработчик выполняет действия, например, отправляет электронное письмо.

new_user_registered = Signal() # сигнал для регистрации нового пользователя

new_order = Signal() # сигнал для обновления статуса заказа


@receiver(reset_password_token_created)
def password_reset_token_created(sender: Type[User], instance: User, reset_password_token: ConfirmEmailToken, **kwargs) -> None:
    """
    Отправляет электронное письмо пользователю, когда происходит сброс пароля.
    
    Args:
        sender: отправитель - модель User 
        instance: пользователь, для которого происходит сброс пароля
        reset_password_token: токен для сброса пароля
        **kwargs: дополнительные параметры
    """
    # send an e-mail to the user 
    msg = EmailMultiAlternatives(
        # title:
        f"Токен сброса пароля для {reset_password_token.user}", 
        # message:
        reset_password_token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    ) # отправляем письмо с токеном для сброса пароля 
    msg.send() # отправляем письмо


@receiver(post_save, sender=User)
def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs) -> None:
    """
    Отправляет письмо с токеном для подтверждения электронного адреса, 
    когда пользователь регистрируется.
    Args:
        sender (Type[User]): отправитель - модель User 
        instance (User): новосозданный пользователь
        created (bool): флаг, что пользователь был создан
        **kwargs: дополнительные параметры
    """
    if created and not instance.is_active: # если пользователь создан и не активен
        # создаем токен для подтверждения электронного адреса 
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk) # возвращает кортеж, содержащий два элемента: сам объект и булево значение, 
                                                                        # указывающее, был ли он создан или уже существовал (заглушка _).
        msg = EmailMultiAlternatives(
            # title:
            f"Токен подтверждения электронного адреса для {instance.email}",
            # message:
            token.key,
            # from:
            settings.EMAIL_HOST_USER,
            # to:
            [instance.email]
        )
        msg.send()


# @receiver(new_order)
# def new_order_signal(user_id: int, **kwargs) -> None:
#     """
#     Отправляет электронное письмо пользователю, когда происходит обновление статуса заказа.
    
#     Args:
#         user_id (int): id пользователя, которому будет отправлено письмо
#         **kwargs: дополнительные параметры
#     """
#     # send an e-mail to the user
#     user = User.objects.get(id=user_id) 

#     msg = EmailMultiAlternatives(
#         # title:
#         f"Обновление статуса заказа",
#         # message:
#         'Заказ сформирован',
#         # from:
#         settings.EMAIL_HOST_USER,
#         # to:
#         [user.email]
#     ) 
#     msg.send()


######################### NEW NEW NEW ########################

@receiver(new_order)
def new_order_signal(user_id: int, order: Order, **kwargs) -> None:
    """
    Отправляет электронное письмо пользователю при изменении статуса заказа.
    Динамически цепляет статус заказа из запроса клиента и интегрирует его в тело письма
    
    Args:
        user_id (int): ID пользователя
        order (Order): Объект заказа
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Получаем человекочитаемое название статуса
        state_display = order.get_state_display()
        
        msg = EmailMultiAlternatives(
            # Заголовок
            f"Обновление статуса заказа №{order.id}",
            # Сообщение с текущим статусом
            f"Статус заказа изменен на: {state_display}",
            # Отправитель
            settings.EMAIL_HOST_USER,
            # Получатель
            [user.email]
        )
        msg.send()
    except User.DoesNotExist:
        print(f"User with id {user_id} not found")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

######################### NEW NEW NEW ########################
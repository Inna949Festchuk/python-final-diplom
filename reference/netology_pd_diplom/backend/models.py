from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _ # функция интернационализации (i18n) 
# gettext_lazy — "ленивая" версия функции перевода (вычисляется только при рендеринге, а не при загрузке модели).
from django_rest_passwordreset.tokens import get_token_generator

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)


# Create your models here.


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    Менеджер полностью переопределяет логику работы с username, используя email как основной идентификатор
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создайте и сохраните пользователя с указанным именем, адресом электронной почты и паролем.
        Args:
            email (str): Обязательное поле. Электронная почта пользователя
            password (str): Пароль (может быть None для незарегистрированных пользователей)
            **extra_fields: Дополнительные атрибуты пользователя
        Returns:
            User: созданный пользователь
        Raises:
            ValueError: если email не указан
        """
        # Валидация обязательного поля
        if not email:
            raise ValueError('The given email must be set')
        # Нормализация email (приведение к нижнему регистру, обрезка пробелов)
        email = self.normalize_email(email)
        # Создание объекта пользователя (использует связанную модель User)
        user = self.model(email=email, **extra_fields)
        # Безопасное хеширование пароля перед сохранением в БД
        user.set_password(password)
        # Сохранение в БД с указанием используемой базы данных
        user.save(using=self._db)
        return user
    

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает обычного пользователя с дефолтными правами.
        
        Особенности:
        - is_staff: False (нет доступа в админку)
        - is_superuser: False (нет прав суперпользователя)
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает суперпользователя с расширенными правами.
        
        Автоматически устанавливает:
        - is_staff: True (доступ в админку)
        - is_superuser: True (полные права)
        - is_active: True (активация без подтверждения email)
        
        Raises:
            ValueError: если права не соответствуют суперпользователю
        """
        # Установка прав суперпользователя
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        # Валидация установленных прав
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    Заменяет стандартный username на email для аутентификации (кастомизация).
    """
    # Убираем обязательные поля по умолчанию (username не используется для входа)
    REQUIRED_FIELDS = []

    # Менеджер объектов с расширенной логикой создания пользователей, так как 
    # используем email как уникальный идентификатор вместо username
    objects = UserManager() # теперь при работе с БД через object можно использовать методы из 
                    # кастомного менеджера UserManager()  - create_user() и create_superuser(), например 
                    # user = User.objects.create_user() или user = User.objects.create_superuser()

    # используем email как уникальный идентификатор вместо username
    USERNAME_FIELD = 'email'

    # Основное поле для аутентификации (уникальное, обязательно для заполнения)
    email = models.EmailField(_('email address'), unique=True)
    # Дополнительные бизнес-поля (необязательные)
    company = models.CharField(
        verbose_name=_('Компания'), 
        max_length=40, 
        blank=True, # разрешаем пустое значение
        help_text=_("Название компании пользователя (для магазинов)"),
        ) 
    position = models.CharField(
        verbose_name=_('Должность'), 
        max_length=40, 
        blank=True,
        help_text=_("Должность в компании (для сотрудников магазинов)"),
        )
    # Валидатор для username (оставлен для совместимости)
    username_validator = UnicodeUsernameValidator()
    # Поле username оставлено для совместимости с материнским AbstractUser, 
    # но не используется для аутентификации
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    # Статус активации (по умолчанию неактивен до подтверждения email)
    is_active = models.BooleanField(
        _('active'),
        default=False, # активируется после подтверждения email
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'),
    )
    # Тип пользователя для разграничения ролей в системе
    type = models.CharField(
        verbose_name=_('Тип пользователя'), 
        choices=USER_TYPE_CHOICES, # ('shop', 'Магазин') или ('buyer', 'Покупатель')
        max_length=5, 
        default='buyer',
        help_text=_("Тип учетной записи (магазин или покупатель)"),
    )

    def __str__(self):
        """Строковое представление с использованием имени и фамилии"""
        return f'{self.first_name} {self.last_name}' if self.first_name else self.email

    class Meta:
        verbose_name = _('Пользователь') 
        verbose_name_plural = _("Список пользователей")
        ordering = ('email',) # сортировка по email по умолчанию
        # Дополнительная защита от дубликатов
        constraints = [
            models.UniqueConstraint(
                fields=['email'], 
                name='unique_email'
            )
        ]


class Shop(models.Model):
 
    objects = models.manager.Manager() # Можно создать кастомный менеджер, который позволит при взаимодействии с базой данных
                                # используя objects применять свои кастомные методы, но здесь используется стандартный менеджер,так как если 
                                # провалиться внутрь него мы увидим заглушку pass, ну или какие-то собственные методы определены с помощью .from_queryset
                                # в субклассе QuerySet 
                                # см. https://docs.djangoproject.com/en/4.1/topics/db/managers/#managers
                                # см. https://docs.google.com/document/d/1_zO0NaMzGqY6ohgqYxi875pghBdFho9RvKxB5fhbjSc/edit?usp=sharing
    name = models.CharField(max_length=50, verbose_name=_('Название'))
    url = models.URLField(verbose_name=_('Ссылка'), null=True, blank=True)
    user = models.OneToOneField(User, verbose_name=_('Пользователь'),
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    state = models.BooleanField(verbose_name=_('статус получения заказов'), default=True) 

    # filename

    class Meta:
        verbose_name = _('Магазин')
        verbose_name_plural = _('Список магазинов')
        ordering = ('-name',) # сортировка по названию по убыванию

    def __str__(self):
        return self.name


class Category(models.Model):
    objects = models.manager.Manager() 
    name = models.CharField(max_length=40, verbose_name=_('Название'))
    shops = models.ManyToManyField(Shop, verbose_name=_('Магазины'), related_name='categories', blank=True)

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Список категорий')
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(max_length=80, verbose_name=_('Название'))
    category = models.ForeignKey(Category, verbose_name=_('Категория'), related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Список продуктов')
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    objects = models.manager.Manager()
    model = models.CharField(max_length=80, verbose_name=_('Модель'), blank=True)
    external_id = models.PositiveIntegerField(verbose_name=_('Внешний ИД'))
    product = models.ForeignKey(Product, verbose_name=_('Продукт'), related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name=_('Магазин'), related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_('Количество'))
    price = models.PositiveIntegerField(verbose_name=_('Цена'))
    price_rrc = models.PositiveIntegerField(verbose_name=_('Рекомендуемая розничная цена'))

    class Meta:
        verbose_name = _('Информация о продукте')
        verbose_name_plural = _("Информационный список о продуктах")
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ] # дополнительная защита от дубликатов 


class Parameter(models.Model):
    objects = models.manager.Manager()
    name = models.CharField(max_length=40, verbose_name=_('Название'))

    class Meta:
        verbose_name = _('Имя параметра')
        verbose_name_plural = _('Список имен параметров')
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    objects = models.manager.Manager()
    product_info = models.ForeignKey(ProductInfo, verbose_name=_('Информация о продукте'),
                                     related_name='product_parameters', blank=True,
                                     on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name=_('Параметр'), related_name='product_parameters', blank=True,
                                  on_delete=models.CASCADE)
    value = models.CharField(verbose_name=_('Значение'), max_length=100)

    class Meta:
        verbose_name = _('Параметр')
        verbose_name_plural = _('Список параметров')
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]
    

class Contact(models.Model):
    objects = models.manager.Manager()
    user = models.ForeignKey(User, verbose_name=_('Пользователь'),
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name=_('Город'))
    street = models.CharField(max_length=100, verbose_name=_('Улица'))
    house = models.CharField(max_length=15, verbose_name=_('Дом'), blank=True)
    structure = models.CharField(max_length=15, verbose_name=_('Корпус'), blank=True)
    building = models.CharField(max_length=15, verbose_name=_('Строение'), blank=True)
    apartment = models.CharField(max_length=15, verbose_name=_('Квартира'), blank=True)
    phone = models.CharField(max_length=20, verbose_name=_('Телефон'))

    class Meta:
        verbose_name = _('Контакты пользователя')
        verbose_name_plural = _("Список контактов пользователя")

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):
    objects = models.manager.Manager()
    user = models.ForeignKey(User, verbose_name=_('Пользователь'),
                             related_name='orders', blank=True,
                             on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(verbose_name=_('Статус'), choices=STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(Contact, verbose_name=_('Контакт'),
                                blank=True, null=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _("Список заказ")
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)

    # @property
    # def sum(self):
    #     return self.ordered_items.aggregate(total=Sum("quantity"))["total"]


class OrderItem(models.Model): # связывает заказ с конкретными товарами (`ProductInfo`) и количеством
    objects = models.manager.Manager()
    order = models.ForeignKey(Order, verbose_name=_('Заказ'), related_name='ordered_items', blank=True,
                              on_delete=models.CASCADE)

    product_info = models.ForeignKey(ProductInfo, verbose_name=_('Информация о продукте'), related_name='ordered_items',
                                     blank=True,
                                     on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_('Количество'))

    class Meta:
        verbose_name = _('Заказанная позиция')
        verbose_name_plural = _("Список заказанных позиций")
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item'),
        ] 


class ConfirmEmailToken(models.Model):
    objects = models.manager.Manager()
    class Meta:
        verbose_name = _('Токен подтверждения Email')
        verbose_name_plural = _('Токены подтверждения Email')

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_('The User which is associated to this password reset token')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('When was this token generated')
    )

    # Ключевое поле, хотя оно и не является первичным ключом модели
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return _("Password reset token for user {user}").format(user=self.user)

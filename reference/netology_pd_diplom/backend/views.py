from distutils.util import strtobool
from typing import Any
from rest_framework.request import Request
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from requests import get
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json # более быстрая альтернатива стандартной библиотеки json
from yaml import load as load_yaml, Loader

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken
from backend.serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderItemSerializer, OrderSerializer, ContactSerializer
from backend.signals import new_user_registered, new_order


class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """

    # Регистрация методом POST
    def post(self, request: Request, *args: Any, **kwargs: Any) -> JsonResponse: # NEW Добавлена аннотация типов
        """
        Process a POST request and create a new user.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        # проверяем, находятся ли все ключи в request.data
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):

            # проверяем пароль на сложность
            # sad = 'asd'
            try:
                validate_password(request.data['password']) # Проверка сложности пароля
            except ValidationError as password_error: # Проверка ошибок пароля NEW
                error_array = []
                for item in password_error:
                    error_array.append(str(item)) # добавление строки (NEW) ошибок пароля в массив error_array 
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}}, status=400) # Отправка клиенту информации об ошибке ввода пароля
            else:
                # проверяем данные пользователя на валидность
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save() # сохраняем данные пользователя в БД (если e-mail уникальный,
                                                    # что проверяется в models.py в классе UserManager в момент записи в БД
                    # Так как пароли должны храниться в безопасном виде. 
                    # Метод set_password() автоматически хеширует пароль из запроса
                    # с использованием алгоритма, установленного в настройках Django (по умолчанию это PBKDF2).
                    user.set_password(request.data['password'])
                    user.save() # сохраняем пользователя и хешированный пароль
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors}, status=400)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=400)


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):
        """
        Подтверждает почтовый адрес пользователя.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        # проверяем, находятся ли все ключи в request.data
        if {'email', 'token'}.issubset(request.data): 
            # Устанавливаем соответствие между парой email-token переданной POST парой email-token, хранящейся в БД
            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True # если токен есть, активируем нового пользователя
                token.user.save() # и сохраняем изменеия в БД
                token.delete() # токен удаляем в целях повышения защиты
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'}, status=400)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=400)


class AccountDetails(APIView):
    """
    Класс для управления данными учетной записи пользователя.

    Methods:
    - get: Retrieve the details of the authenticated user.
    - post: Update the account details of the authenticated user.

    Attributes:
    - None
    """

    # получить данные
    def get(self, request: Request, *args, **kwargs):
        """
        Retrieve the details of the authenticated user.

        Args:
        - request (Request): The Django request object.

        Returns:
        - Response: The response containing the details of the authenticated user.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        serializer = UserSerializer(request.user) # сериализуем пользователя
        return Response(serializer.data)

    # Редактирование методом POST
    def post(self, request, *args, **kwargs):
        """
        Update the account details of the authenticated user.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        # проверяем обязательные аргументы
        if 'password' in request.data:
            # errors = {} 
            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = [] # создаем список для хранения ошибок
                for item in password_error: # добавление строки ошибок пароля в массив error_array
                    error_array.append(item) # добавление строки ошибок пароля в массив error_array
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                request.user.set_password(request.data['password']) # записываем новый пароль в БД
        user_serializer = UserSerializer(request.user, data=request.data, partial=True) # сериализуем пользователя (data - обновляемые данные
        # partial=True - не все поля необходимо передавать, и если некоторые поля отсутствуют, это не вызовет ошибку валидации)
        if user_serializer.is_valid(): # если данные валидны
            user_serializer.save() # сохраняем изменения в БД
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """

    # Авторизация методом POST
    def post(self, request, *args, **kwargs):
        """
        Создание токена аутентификации для активированных пользователей.

        Args:
            request (Request): The Django request object.

        Returns:
            JsonResponse: The response indicating the status of the operation and any errors.
        """
        if {'email', 'password'}.issubset(request.data): # проверяем, находятся ли все ключи в request.data
            user = authenticate(request, username=request.data['email'], password=request.data['password']) # сверяем учетные данные пользователя из запроса с теми, что хранятся в БД 
                                                                # и возвращает объект пользователя, если аутентификация по имени и паролю прошла успешно

            if user is not None: # если пользователь найден
                if user.is_active: # если пользователь активирован (заодно в админке выбрать этот пользователь buyer или shop)
                    token, _ = Token.objects.get_or_create(user=user) # создаем токен (этот токен будет использоваться для аутентификации пользователя в будущих запросах) 

                    return JsonResponse({'Status': True, 'Token': token.key}, status=200) # возвращаем токен клиенту

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'}, status=400) # если пользователь не найден

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=400) # если не указаны все необходимые аргументы


class CategoryView(ListAPIView): 
    """
    Класс для просмотра списка категорий товаров
    """
    queryset = Category.objects.all() # выбираем все категории товаров
    serializer_class = CategorySerializer # сериализуем их 


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.filter(state=True) # фильтруем магазины по статусу готовности к получению заказов, т.е. магазин открыт(закрыт)
    serializer_class = ShopSerializer


class ProductInfoView(APIView):
    """
    Класс для поиска продуктов.

    Methods:
    - get: Retrieve the product information based on the specified filters.

    Attributes:
    - None
    """

    def get(self, request: Request, *args, **kwargs):
        """
        Клас для поиска продуктов по фильтрам.

        Args:
        - request (Request): The Django request object.

        Returns:
        - Response: The response containing the product information.
        """
        # Объект Q используется для создания сложных запросов с помощью логических операторов
        query = Q(shop__state=True) # фильтруем магазины по статусу готовности к получению заказов
        shop_id = request.query_params.get('shop_id') # получаем id магазина из параметров запроса
        category_id = request.query_params.get('category_id') # получаем id категории из параметров запроса

        if shop_id: # если id магазина указан
            query = query & Q(shop_id=shop_id) # фильтруем продукты по id магазина

        if category_id: # если id категории указан
            query = query & Q(product__category_id=category_id) # фильтруем продукты по id категории

        # фильтруем объекты ProductInfo по сформированному запросу query и отбрасываем дубликаты
        queryset = ProductInfo.objects.filter(
            query).select_related( # информация о связанных магазинах (shop) и категориях продуктов (product__category) 
                                # будет загружена джоином с основным объектом ProductInfo (т.е. в одном запросе к БД что эффективно)
            'shop', 'product__category').prefetch_related( # В отличие от select_related, метод выполняет отдельные запросы для получения связанных объектов, 
                                                # а затем соединяет их в Python с объектом ProductInfo. 
                                                # Здесь он извлекает параметры каждого продукта и их значения и соединяет с информацией о продукте.
            'product_parameters__parameter').distinct() # удаления дублирующихся записей из результата выборки

        # ПОМЕТКА! prefetch_related - выполняет отдельные запросы для основной модели и для связанных объектов. Затем результаты объединяются в Python.
        # ПОМЕТКА! select_related - использует SQL JOIN для выполнения запроса и получения связанных объектов одновременно с основным объектом.

        # ЗАМЕТКА
        # Жадная загрузка (чтобы уменьшить количество обращений к базе данных)
        # всех связей из поля 'shop' (это id магазинов модели Shop) и из поля 'product' -
        # это id продуктов соответствующей категории (поле 'category' модели Product, 
        # содержит id категорий, связанной модели Category). 

        # поле 'product_parameters' содержит id, связывающие значения параметров продуктов, 
        # с ProductInfo, а поле 'parameter' содержит id названий этих параметров из модели Parametr.

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    """
    A class for managing the user's shopping basket.

    Methods:
    - get: Retrieve the items in the user's basket.
    - post: Add an item to the user's basket.
    - put: Update the quantity of an item in the user's basket.
    - delete: Remove an item from the user's basket.

    Attributes:
    - None
    """

    # получить корзину
    def get(self, request, *args, **kwargs):
        """
        Retrieve the items in the user's basket.

        Args:
        - request (Request): The Django request object.

        Returns:
        - Response: The response containing the items in the user's basket.
        """
        if not request.user.is_authenticated: # проверяется, аутентифицирован ли пользователь
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        
        # Извлекаем заказы из корзины и рассчитываем итоговую стоимость заказов в корзине
        basket = Order.objects.filter( # Из модели Order извлекаются заказы пользователя с заданным user_id, у которых состояние равно "basket" (корзина)
            user_id=request.user.id, state='basket').prefetch_related( # заранее извлекаем связанные данные, 
                                            # что минимизирует количество запросов к базе данных и улучшает производительность
            'ordered_items__product_info__product__category', # у id покупателя заказ, количество заказанных товаров их характеристики, названия и категории.
            'ordered_items__product_info__product_parameters__parameter').annotate( # параметры товаров и их значения.
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
            # далее рассчитываем итоговую стоимость заказа total_sum - умножаем количество заказанных товаров на их цену и суммируем общую цену
        serializer = OrderSerializer(basket, many=True) # сериализуем все заказы в корзине в формат JSON 
        return Response(serializer.data)

    # редактировать корзину
    def post(self, request, *args, **kwargs):
        """
        Добавить товары в корзину пользователя (покупателя).

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: # проверяется, аутентифицирован ли пользователь
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items') # из байт-строки в формате JSON получаем данные о товарах из запроса
        if items_sting: # если данные о товарах указаны в запросе
            try:
                # 
                items_dict = load_json(items_sting) # преобразуем данные о товарах из строки JSON в словарь python 
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else: # если JSON-строка при преобразовании в словарь python была валидна
                # добавляем товары в корзину: в моделе Order создаем новый заказ для пользователя с id
                # и присваеваем ему статус "корзина"
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket') # создаем корзину, как экземпляр модели Order 
                
                # ЗАМЕТКА
                # Если заказ с указанными параметрами существует, basket будет ссылаться на этот существующий объект.
                # Если заказа нет, будет создан новый Order, и basket будет указывать на этот новый объект.
                # _: Параметр, который принимает значение True, если объект был создан, и False, если объект был найден. 
                # Этот параметр не используется в дальнейшем коде, так как он обозначен знаком подчеркивания (зачастую 
                # это означает, что значение не нужно).
                
                objects_created = 0 # счетчик добавленных в корзину товаров  
                for order_item in items_dict: # для каждого товара из словаря items_dict ...
                    order_item.update({'order': basket.id}) # ... добавляем id заказа (в словарь order_item добавляем/обновляем ключ order со значением basket.id) 
                    serializer = OrderItemSerializer(data=order_item) # создаем экземпляр сериализатора OrderItemSerializer с данными из order_item
                    if serializer.is_valid(): # если данные валидны
                        try:
                            serializer.save() # сохраняем данные в модели OrderItem 
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1 # увеличиваем счетчик

                    else:

                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

                return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        """
        Удалить товары из корзины пользователя (покупателя).

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован выкидываем 403
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items') # из байт-строки в формате JSON получаем данные о товарах из запроса
        if items_sting: # если данные о товарах указаны в запросе
            items_list = items_sting.split(',') # сплитуем строку по разделителю "," получая на выходе список id товаров для удаления
            # Получаем корзину пользователя
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket') 
            query = Q() # создаем пустое условие фильтрации.
            objects_deleted = False # Флаг для отслеживания, были ли удалены товары.
            for order_item_id in items_list: # для каждого id товара в списке
                if order_item_id.isdigit(): # Проверяем, является ли идентификатор числом.
                    # Добавляем условие для удаления в запрос Q ... 
                    query = query | Q(order_id=basket.id, id=order_item_id) # которое используется для фильтрации модели 
                                            # OrderItem по идентификатору заказа и идентификатору товара ниже.
                    # СПРАВКА
                    # Если в переменной items_list находятся значения [3, 5], и id корзины basket.id = 1, 
                    # запрос query будет последовательно строиться так:
                    # После первого элемента: Q(order_id=1, id=3)
                    # После второго элемента: Q(order_id=1, id=3) | Q(order_id=1, id=5)
                    # Таким образом, в результате вы получите один объект Q, 
                    # который соответствует всем указанным идентификаторам в корзине. 

                    objects_deleted = True # Устанавливаем флаг, что у нас есть объекты для удаления.

            if objects_deleted: # Если есть объекты для удаления, выполняем удаление.
                deleted_count = OrderItem.objects.filter(query).delete()[0] # Удаляем объекты, соответствующие условию в query из OrderItem.
                # СПРАВКА
                # Метод delete() возвращает кортеж (количество удаленных записей, словарь, где ключами являются модели, а значениями — количество удаленных записей для каждой модели)
                # мы используем [0], чтобы извлечь только первый элемент (количество удаленных объектов) из возвращаемого кортежа
                # для формирования ответа пользователю
                
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # добавить позиции в корзину
    def put(self, request, *args, **kwargs):
        """
        Обновление товаров в корзине пользователя (покупателя).

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован выкидываем 403
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items') # из байт-строки в формате JSON получаем данные о товарах из запроса
        if items_sting: # если данные о товарах указаны в запросе
            try:
                items_dict = load_json(items_sting) # преобразуем в словарь 
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket') # Получаем заказ пользователя
                objects_updated = 0 # счетчик обновленных объектов
                for order_item in items_dict: # для каждого товара в запросе
                    if type(order_item['id']) == int and type(order_item['quantity']) == int: # проверяем, что идентификатор и количество являются целыми числами
                        objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity']) # обновляем количество товара 

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerUpdate(APIView):
    """
    A class for updating partner information.

    Methods:
    - post: Update the partner information.

    Attributes:
    - None
    """

    def post(self, request, *args, **kwargs):
        """
        Update the partner price list information.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403) # возвращаем ошибку 403 и сообщение о необходимости аутентификации

        if request.user.type != 'shop': # если пользователь не магазин
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403) # возвращаем ошибку 403 и сообщение о необходимости быть магазином (назначается в админ панеле)
        # Загружаем товары из .yml который размещен по адресу с url
        url = request.data.get('url') # получаем url из запроса пользователя 
        if url: # если url указан
            validate_url = URLValidator() # создаем валидатор для url 
            try:
                validate_url(url) # проверяем валидность url
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)}, status=400) # возвращаем ошибку 400 и сообщение об ошибке валидации url
            else:
                stream = get(url).content # получаем контент из yaml-файла размещенного по некоторому url 

                data = load_yaml(stream, Loader=Loader) # декодируем контент и преобразуем в словарь 

                shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id) # получаем или создаем магазин с названием из data['shop'] и авторизированным пользователем request.user.id
                
                # ЗАМЕТКА:
                # request:
                # Это объект HttpRequest, который передается в представление в Django. Он содержит всю информацию о текущем запросе, включая данные о пользователе, 
                # пришедшие из HTTP-заголовков, параметры URL, данные и тд
                # request.user:
                # Это атрибут объекта request, который возвращает объект пользователя (класса User) для текущего запроса (если пользователь аутенифицирован is_authenticated = True).
                # request.user.id:
                # Это доступ к атрибуту id объекта пользователя. Он возвращает уникальный идентификатор пользователя в базе данных. 

                for category in data['categories']: # проходим по категориям в data['categories']
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name']) # получаем или создаем категорию с id и name из category
                    category_object.shops.add(shop.id) # добавляем магазин в категорию
                    category_object.save() # сохраняем изменения в категории 
                ProductInfo.objects.filter(shop_id=shop.id).delete() # удаляем из прайса все загруженные в магазин shop.id товары 
                for item in data['goods']: # проходим по товарам в data['goods']
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category']) # получаем или создаем продукт с названием item['name'] и категорией item['category']

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id) # создаем информацию о продукте
                    for name, value in item['parameters'].items(): # проходим по ключам и значениям в item['parameters']
                        parameter_object, _ = Parameter.objects.get_or_create(name=name) # получаем или создаем параметр товара с названием name
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value) # создаем значение параметра товара

                return JsonResponse({'Status': True}, status=200) # возвращаем сообщение об успешном обновлении прайса 

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=400) # возвращаем ошибку 400 и сообщение о необходимости указать все необходимые аргументы


class PartnerState(APIView):
    """
       A class for managing partner state.

       Methods:
       - get: Retrieve the state of the partner.

       Attributes:
       - None
       """
    # получить текущий статус
    def get(self, request, *args, **kwargs):
        """
        Retrieve the state of the partner.

        Args:
        - request (Request): The Django request object.

        Returns:
        - Response: The response containing the state of the partner.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):
        """
               Update the state of a partner.

               Args:
               - request (Request): The Django request object.

               Returns:
               - JsonResponse: The response indicating the status of the operation and any errors.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state)) # преобразует строку в логическое значение True или False 
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками
     Methods:
    - get: Retrieve the orders associated with the authenticated partner.

    Attributes:
    - None
    """

    def get(self, request, *args, **kwargs):
        """
               Retrieve the orders associated with the authenticated partner.

               Args:
               - request (Request): The Django request object.

               Returns:
               - Response: The response containing the orders associated with the partner.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        
        # ПОМЕТКА! prefetch_related - выполняет отдельные запросы для основной модели и для связанных объектов. Затем результаты объединяются в Python.
        # ПОМЕТКА! select_related - использует SQL JOIN для выполнения запроса и получения связанных объектов одновременно с основным объектом.

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class ContactView(APIView):
    """
       Класс для управления контактной информацией.

       Methods:
       - get: Retrieve the contact information of the authenticated user.
       - post: Create a new contact for the authenticated user.
       - put: Update the contact information of the authenticated user.
       - delete: Delete the contact of the authenticated user.

       Attributes:
       - None
       """

    # получить мои контакты
    def get(self, request, *args, **kwargs):
        """
        Retrieve the contact information of the authenticated user.

        Args:
        - request (Request): The Django request object.

        Returns:
        - Response: The response containing the contact information.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(
            user_id=request.user.id) # выбираем все контакты, связанные с аутентифицированным пользователем
        serializer = ContactSerializer(contact, many=True) # сериализуем контакты (возвращает QuerySet с несколькими записями) 
        return Response(serializer.data)

    # добавить новый контакт
    def post(self, request, *args, **kwargs):
        """
        Create a new contact for the authenticated user.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован 
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'city', 'street', 'phone'}.issubset(request.data): # если есть все необходимые аргументы
            request.data._mutable = True # изменяем мутабельность чтобы ...
            request.data.update({'user': request.user.id}) # добавить в request.data новый ключ user, который содержит идентификатор аутентифицированного пользователя
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid(): # если данные валидны
                serializer.save() # сохраняем контактные данные в базу данных
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить контакт
    def delete(self, request, *args, **kwargs):
        """
        Delete the contact of the authenticated user.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items') # получаем список id контактов
        if items_sting: # если список id контактов указан
            items_list = items_sting.split(',') #  сплитуем строку по разделителю "," получая на выходе список id контактов для удаления
            query = Q() # создаем пустое условие фильтрации
            objects_deleted = False # флаг удаленных объектов
            for contact_id in items_list: # перебираем список id контактов
                if contact_id.isdigit(): # если id контакта является числом
                    # Добавляем условие для удаления в запрос Q ... 
                    query = query | Q(user_id=request.user.id, id=contact_id) # которое используется для фильтрации модели Contact 
                                            # по идентификатору пользователя и идентификатору контакта ниже. 
                    objects_deleted = True # устанавливаем флаг удаленных объектов
            if objects_deleted: # если True 
                deleted_count = Contact.objects.filter(query).delete()[0] # удаляем объекты по запросу query
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # редактировать контакт
    def put(self, request, *args, **kwargs):
        """
        Update the contact information of the authenticated user.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: 
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'id' in request.data: # если id контакта указан
            if request.data['id'].isdigit(): # если id контакта является числом
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first() # фильтруем контакты по заданному id 
                if contact: # если контакт найден
                    serializer = ContactSerializer(contact, data=request.data, partial=True) # обновляем контакт (data - данные для обновления,
                    # partial=True - не все поля необходимо передавать, и если некоторые поля отсутствуют, это не вызовет ошибку валидации)
                    if serializer.is_valid(): # если объект сериализаторы содержит валидные данные
                        serializer.save() # записываем данные в БД
                        return JsonResponse({'Status': True})
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class OrderView(APIView):
    """
    Класс для получения и размешения заказов пользователями (покупателями)
    Methods:
    - get: Retrieve the details of a specific order.
    - post: Create a new order.
    - put: Update the details of a specific order.
    - delete: Delete a specific order.

    Attributes:
    - None
    """

    # получить мои заказы
    def get(self, request, *args, **kwargs):
        """
        Получить данные о заказах пользователя(покупателя).

        Args:
        - request (Request): The Django request object.

        Returns:
        - Response: The response containing the details of the order.
        """
        if not request.user.is_authenticated: # 
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        # фильтруем заказы по id пользователя(покупателя)
        # исключая из результата фильтрации заказы со статусом "в корзине"...
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related( # добавляем связанную предварительную выборку:
            'ordered_items__product_info__product__category', # заказанные_товары__информация_о_продукте__категория_продукта,
                                    # заказанные_товары__информация_о_продукте__параметры_продукта_параметр
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate( # выбираем связанные контакты и добавляем аннотацию 
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct() # рассчитываем общую стоимость заказа, 
                                                                                                # перемножая количество и цену товара и удаляем дубликаты из результата выборки
        # ПОМЕТКА! prefetch_related - выполняет отдельные запросы для основной модели и для связанных объектов. Затем результаты объединяются в Python.
        # ПОМЕТКА! select_related - использует SQL JOIN для выполнения запроса и получения связанных объектов одновременно с основным объектом.

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # разместить новый заказ из корзины
    def post(self, request, *args, **kwargs):
        """
        Оформить заказ и отправить уведомление магазину.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated: # если пользователь не аутентифицирован
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data): # если id заказа и id контакта указаны в запросе
            if request.data['id'].isdigit(): # если id заказа является числом
                try: # пытаемся обновить заказ
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        state='new') # фильтруем заказы, принадлежащие текущему аутентифицированному пользователю
                                # по идентификатору заказа, который передан в запросе
                                # в соответствии с переданным идентификатором контакта обновляем поле contact_id,
                                # устанавливая связь заказа с контактом пользователя-покупателя
                                # меняем статус заказа c "basket" на "new"
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
                else:
                    if is_updated:
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

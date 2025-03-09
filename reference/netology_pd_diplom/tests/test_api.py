# Тесты сфокусированны на проверке API, а модели проверяются 
# косвенно (т.е. в текущих тестах проверяется интеграция — например, 
# при добавлении товаров в корзину создаётся OrderItem, 
# но нет юнит-тестов конкретно для модели OrderItem).

import json # для работы с JSON
import pytest # для написания тестов
from django.urls import reverse # для работы с пространством имен
# APIClient - тестовый клиент DRF, который позволяет имитировать 
# HTTP-запросы к разработанному API в тестах
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model # для получения модели пользователя
from model_bakery import baker # для создания тестовых данных
from unittest.mock import patch # для работы с моками
from backend.models import Shop, Category, Product, ProductInfo, Order, Contact, ConfirmEmailToken

User = get_user_model() # получаем модель пользователя

# Фикстура для клиента API
@pytest.fixture
def client():
    """
    Фикстура для клиента API.
    """
    return APIClient() # клиент для тестирования API 

# Общая фикстура для аутентифицированного пользователя
@pytest.fixture
def authenticated_user(client):
    """
    Фикстура для аутентифицированного пользователя.
    """
    user = baker.make(User) # создаем тестового пользователя
    client.force_authenticate(user=user) # Принудительная аутентификация пользователя
    return user

# Тесты для RegisterAccount
@pytest.mark.django_db
class TestRegisterAccount:
    """
    Класс для тестирования регистрации пользователя.
    """
    def test_register_missing_fields(self, client):
        """
        Проверяем, что регистрация пользователя не проходит, если не указаны все обязательные поля.
        """
        url = reverse('backend:user-register') # получаем url эндпоинта RegisterAccount из пространства имен
        response = client.post(url, {}) # отправляем POST-запрос
        assert response.status_code == 400 # проверка статуса
        assert 'Errors' in response.json() # проверяем, что в ответе есть ключ 'Errors' 

    def test_register_invalid_password(self, client):
        """
        Проверяем, что регистрация пользователя не проходит, если пароль невалиден.
        """
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'password': '123', 
            'company': 'TestCo',
            'position': 'Manager'
        } # создаем словарь с невалидным паролем
        url = reverse('backend:user-register') # получаем url эндпоинта RegisterAccount из пространства имен
        response = client.post(url, data) # отправляем POST-запрос
        assert response.status_code == 400 # проверка статуса
        assert 'password' in response.json()['Errors'] # проверяем, что в ответе есть ключ 'password' внутри ключа 'Errors'

    def test_register_success(self, client):
        """
        Проверяем, что регистрация пользователя проходит успешно.
        """
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'password': 'TestPass123!',
            'company': 'TestCo',
            'position': 'Manager'
        } # создаем словарь с валидным паролем
        url = reverse('backend:user-register')
        response = client.post(url, data)
        assert response.status_code == 200
        assert response.json()['Status'] is True # проверяем, что в ответе есть ключ 'Status' со значением True

# Тесты для ConfirmAccount
@pytest.mark.django_db # декоратор для работы с базой данных
class TestConfirmAccount:
    """
    Класс для тестирования подтверждения учетной записи.
    """
    def test_confirm_invalid_token(self, client):
        """
        Проверяем, что подтверждение учетной записи не проходит, если указан невалидный токен.
        """
        user = baker.make(User, email='test@test.com', is_active=False) # создаем тестового пользователя
        baker.make(ConfirmEmailToken, user=user) # создаем токен
        url = reverse('backend:user-register-confirm') # получаем url эндпоинта ConfirmAccount из пространства имен
        data = {'email': 'test@test.com', 'token': 'wrong_token'} # создаем словарь с невалидным токеном
        response = client.post(url, data) 
        assert response.status_code == 400
        assert 'Errors' in response.json() # проверяем, что в ответе есть ключ 'Errors'

    def test_confirm_success(self, client):
        """
        Проверяем, что подтверждение учетной записи проходит успешно.
        """
        user = baker.make(User, email='test@test.com', is_active=False) # создаем тестового пользователя
        token = baker.make(ConfirmEmailToken, user=user) # создаем токен
        url = reverse('backend:user-register-confirm') # получаем url эндпоинта ConfirmAccount из пространства имен
        data = {'email': 'test@test.com', 'token': token.key} # создаем словарь с валидным токеном
        response = client.post(url, data)
        user.refresh_from_db() # обновляем данные пользователя из базы данных 
        assert response.status_code == 200
        assert user.is_active is True # проверяем, что пользователь активирован (поле is_active установлено в True)

# Тесты для LoginAccount
@pytest.mark.django_db
class TestLoginAccount:
    """
    Класс для тестирования входа в систему.
    """
    def test_login_invalid_credentials(self, client):
        """
        Проверяем, что вход в систему не проходит, если указаны невалидные учетные данные.
        """
        user = baker.make(User, email='test@test.com', password='TestPass123!', is_active=True) # создаем тестового пользователя (для авторизации он должен быть активирован) 
        user.set_password(user.password) # устанавливаем пароль
        user.save() # сохраняем его в базе данных
        url = reverse('backend:user-login') # получаем url эндпоинта LoginAccount из пространства имен
        data = {'email': 'test@test.com', 'password': 'WrongPass'} # создаем словарь с невалидным паролем
        response = client.post(url, data) 
        assert response.status_code == 400
        assert 'Errors' in response.json() # проверяем, что в ответе есть ключ 'Errors'

    def test_login_success(self, client):
        """
        Проверяем, что вход в систему проходит успешно.
        """
        user = baker.make(User, email='test@test.com', password='TestPass123!', is_active=True)
        user.set_password(user.password)
        user.save()
        url = reverse('backend:user-login')
        data = {'email': 'test@test.com', 'password': 'TestPass123!'} # создаем словарь с валидным паролем
        response = client.post(url, data)
        assert response.status_code == 200
        assert 'Token' in response.json() # проверяем, что в ответе есть ключ 'Token'

# Тесты для PartnerUpdate
@pytest.mark.django_db
class TestPartnerUpdate:
    """
    Класс для тестирования обновления партнера.
    """
    def test_partner_update_permission(self, client):
        """
        Проверяем, что обновление партнера доступно только для магазинов.
        """
        user = baker.make(User, type='buyer') # назначаем пользователю тип 'buyer' - покупатель
        client.force_authenticate(user=user) # Принудительная аутентификация пользователя
        url = reverse('backend:partner-update') # получаем url эндпоинта PartnerUpdate
        response = client.post(url, {}) # отправляем POST-запрос
        assert response.status_code == 403
        assert response.json()['Error'] == 'Только для магазинов' # проверяем, что в ответе есть ключ 'Error' со значением 'Только для магазинов'

    def test_unauthenticated_user(self, client):
        """
        Проверяем, что обновление партнера доступно только для 
        зарегистрированных пользователей.
        """
        url = reverse('backend:partner-update')
        response = client.post(url, {})
        assert response.status_code == 403
        assert response.json()['Error'] == 'Log in required' # проверяем, что в ответе есть ключ 'Error' со значением 'Требуется вход'

    def test_partner_update_invalid_url(self, client):
        """
        Проверяем, что обновление партнера доступно только для 
        зарегистрированных пользователей с правильными учетными данными.
        """
        user = baker.make(User, type='shop') # назначаем пользователю тип 'shop' - магазин
        client.force_authenticate(user=user) # Принудительная аутентификация пользователя
        url = reverse('backend:partner-update') # получаем url эндпоинта PartnerUpdate
        data = {'url': 'invalid-url'} # создаем словарь с невалидным url
        response = client.post(url, data) # отправляем POST-запрос
        assert response.status_code == 400
        assert 'Error' in response.json() # проверяем, что в ответе есть ключ 'Error'

    def test_partner_update_missing_url(self, client):
        """
        Проверяем, что обновление партнера доступно только для 
        зарегистрированных пользователей с полными учетными данными.
        """
        user = baker.make(User, type='shop')
        client.force_authenticate(user=user) # Принудительная аутентификация пользователя
        url = reverse('backend:partner-update')
        response = client.post(url, {})
        assert response.status_code == 400
        assert response.json()['Errors'] == 'Не указаны все необходимые аргументы' 

    @patch('backend.views.get')  # подменяем метод `requests.get` с помощью Mock для изоляции теста от реальных HTTP-запросов
    @patch('backend.views.load_yaml')  # подменяем функцию `load_yaml`, которая парсит YAML-файлы
    def test_successful_update(self, mock_load_yaml, mock_get, client):
        """
        Проверяем, что обновление партнера проходит успешно.
        mock_load_yaml - мокирование функции `load_yaml`, которая парсит YAML-файлы
        mock_get - мокирование метода `requests.get`, чтобы вернуть заранее заданные данные
        """
        user = baker.make(User, type='shop') # назначаем пользователю тип 'shop' - магазин
        client.force_authenticate(user=user) # принудительная аутентификация пользователя
        mock_load_yaml.return_value = {
            'shop': 'Test Shop',
            'categories': [{'id': 1, 'name': 'Category 1'}],
            'goods': [{
                'id': 1,
                'name': 'Test Product',
                'model': 'Model X',
                'category': 1,
                'price': 100,
                'price_rrc': 150,
                'quantity': 10,
                'parameters': {'color': 'red'}
            }]
        } # заранее задаем данные
        mock_get.return_value.content = b'mock-content' # мокирование данных, которые возвращаются как байтовая строка
        url = reverse('backend:partner-update') # получаем url эндпоинта PartnerUpdate
        data = {'url': 'http://example.com/test.yml'} # мокированный URL прайс-листа
        response = client.post(url, data, format='json') # отправляем POST-запрос
        assert response.status_code == 200
        assert response.json()['Status'] is True # проверяем, что в ответе есть ключ 'Status' со значением True

# Тесты для BasketView
@pytest.mark.django_db
class TestBasketView:
    """
    Класс для тестирования BasketView (корзина).
    """
    @pytest.fixture
    def setup_data(self):
        """
        Фикстура для создания необходимых данных для тестирования.
        """
        user = baker.make(User) # создаем тестового пользователя
        category = baker.make(Category) # создаем тестовую категорию
        shop = baker.make(Shop) # создаем тестовый магазин
        product = baker.make(Product, category=category) # создаем тестовый товар
        product_info = baker.make(ProductInfo, product=product, shop=shop) # создаем тестовую информацию о продукте
        return user, product_info # возвращаем созданные данные

    def test_basket_access_unauthorized(self, client):
        """
        Проверяем доступ к корзине для неавторизованных пользователей.
        """
        url = reverse('backend:basket')
        response = client.get(url)
        assert response.status_code == 403
        assert response.json()['Error'] == 'Log in required'

    def test_basket_add_items(self, client, setup_data):
        """
        Проверяем добавление товаров в корзину для авторизованных пользователей.
        """
        user, product_info = setup_data # получаем данные из фикстуры
        client.force_authenticate(user=user) # аутентификация пользователя
        payload = {"items": json.dumps([{"product_info": product_info.id, "quantity": 2}])} # подготавливаем данные для запроса в формате JSON 
        response = client.post(reverse('backend:basket'), data=payload, format='json') # отправляем POST-запрос
        assert response.status_code == 200
        assert response.json() == {'Status': True, 'Создано объектов': 1} # проверяем, что в ответе есть ключ 'Status' со значением True и ключ 'Создано объектов' со значением 1

# Тесты для OrderView
@pytest.mark.django_db
class TestOrderView:
    """
    Класс для тестирования OrderView (заказы).
    """
    @pytest.fixture
    def setup_order(self):
        """
        Фикстура для создания необходимых данных для тестирования.
        """
        user = baker.make(User) # создаем тестового пользователя
        contact = baker.make(Contact, user=user) # создаем тестовый контакт
        order = baker.make(Order, user=user, state='basket') # создаем тестовый заказ
        return user, contact, order

    def test_order_create_success(self, client, setup_order):
        """
        Проверяем успешное создание заказа.
        """
        user, contact, order = setup_order # получаем данные из фикстуры
        client.force_authenticate(user=user) # аутентификация пользователя
        response = client.post(
            reverse('backend:order'),
            {'id': str(order.id), 'contact': contact.id},
            format='json'
        ) # отправляем POST-запрос с данными об заказе и контакте 
        assert response.status_code == 200
        assert response.json() == {'Status': True} # проверяем, что в ответе есть ключ 'Status' со значением True

    def test_order_create_not_found(self, client):
        """
        Проверяем, что заказ отсутствует в базе данных при неправильном ID для поиска.
        """
        user = baker.make(User) # создаем тестового пользователя
        contact = baker.make(Contact, user=user) # создаем тестовый контакт
        client.force_authenticate(user=user) # аутентификация пользователя
        response = client.post(
            reverse('backend:order'),
            {'id': '999', 'contact': contact.id},
            format='json'
        ) # отправляем POST-запрос с неправильным ID заказа
        assert response.status_code == 404
        assert response.json() == {'Status': False, 'Errors': 'Заказ не найден'} # проверяем, что в ответе есть ключ 'Status' со значением False и ключ 'Errors' со значением 'Заказ не найден'

    def test_order_create_unauthenticated(self, client):
        """
        Проверяем, что заказ не создается, если пользователь не аутентифицирован.
        """
        response = client.post(reverse('backend:order'), {}) 
        assert response.status_code == 403
        assert response.json() == {'Status': False, 'Error': 'Log in required'} # проверяем, что в ответе есть ключ 'Status' со значением False и ключ 'Error' со значением 'Log in required'

    def test_order_create_invalid_data(self, client):
        """
        Проверяем, что заказ не создается с невалидными данными.
        """
        user = baker.make(User) # создаем тестового пользователя
        client.force_authenticate(user=user) # аутентификация пользователя
        response = client.post(
            reverse('backend:order'),
            {'id': 'invalid_id', 'contact': 1},
            format='json'
        ) # отправляем POST-запрос с невалидными данными
        assert response.status_code == 400
        assert 'Errors' in response.json() # проверяем, что в ответе есть ключ 'Errors'

    def test_missing_required_fields(self, client):
        """
        Проверяем, что заказ не создается, если не указаны все необходимые аргументы.
        """
        user = baker.make(User) # создаем тестового пользователя
        client.force_authenticate(user=user) # аутентификация пользователя
        response = client.post(reverse('backend:order'), {}, format='json') # отправляем POST-запрос без необходимых аргументов
        assert response.status_code == 400
        assert response.json() == {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}

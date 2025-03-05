from django.test import TestCase

# Create your tests here.

import pytest
from django.urls import reverse # для работы с пространством имен
# APIClient - тестовый клиент DRF, который позволяет имитировать 
# HTTP-запросы к разработанному API в тестах
from rest_framework.test import APIClient
from rest_framework.test import APITestCase # для упрощения написания тестов
from django.contrib.auth import get_user_model
from model_bakery import baker # для создания тестовых данных
from unittest.mock import patch # для работы с моками
# from requests import get
# from django.core.validators import URLValidator
# from django.core.exceptions import ValidationError
from backend.models import Shop, Category, Product, ProductInfo, Order, Contact, ConfirmEmailToken


User = get_user_model()
client = APIClient()


# Тесты для RegisterAccount (регистрация пользователя)
@pytest.mark.django_db # сообщает системе тестирования pytest, что данный тест будет взаимодействовать с базой данных
class TestRegisterAccount(APITestCase):
    def test_register_missing_fields(self):
        """
        Тесты, для регистрации пользователя. Запрос с отсутствующими полями приводят к ошибке 400
        """
        url = reverse('backend:user-register') # получаем url эндпоинта RegisterAccount из пространства имен
        response = self.client.post(url, {}) # отправка запроса на эндпоинт RegisterAccount
        assert response.status_code == 400 # проверка статуса
        assert 'Errors' in response.json() # проверка наличия ключа 'Errors'

    def test_register_invalid_password(self):
        """
        Тесты, для регистрации пользователя. Запрос с невалидным паролем приводят к ошибке 400
        """
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'password': '123', 
            'company': 'TestCo',
            'position': 'Manager'
        } # передаем неправильные данные
        url = reverse('backend:user-register') 
        response = self.client.post(url, data)
        assert response.status_code == 400 # проверка статуса
        assert 'password' in response.json()['Errors'] # проверка наличия 'password'

    def test_register_success(self):
        """
        Проверяет успешную регистрацию пользователя.
        Дается допустимый набор аргументов, и ответ проверяется на наличие кода статуса 200
        и ключа «Статус» со значением True.
        """
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'password': 'TestPass123!',
            'company': 'TestCo',
            'position': 'Manager'
        } # передаем правильные данные
        url = reverse('backend:user-register') 
        response = self.client.post(url, data)
        assert response.status_code == 200 # проверка статуса
        assert response.json()['Status'] is True # проверка значения ключа 'Status'


# Тесты для ConfirmAccount (подтверждение учетной записи и активация учетной записи)
@pytest.mark.django_db # сообщает системе тестирования pytest, что данный тест будет взаимодействовать с базой данных
class TestConfirmAccount(APITestCase):
    def test_confirm_invalid_token(self):
        """
        Тестирует, что подтверждение учетной записи с недействительным токеном приводит к ответу 400.
        """
        user = baker.make(User, email='test@test.com', is_active=False) # создаем тестового пользователя
        token = baker.make(ConfirmEmailToken, user=user) # тестовый токен не создаем а передаем 'wrong_token'
        url = reverse('backend:user-register-confirm') # получаем url эндпоинта ConfirmAccount из пространства имен
        data = {'email': 'test@test.com', 'token': 'wrong_token'} # передаем неправильный токен 'wrong_token'
        response = self.client.post(url, data) # отправляем запрос
        assert response.status_code == 400 # проверяем код ответа (должна быть ошибка 400)
        assert 'Errors' in response.json() # проверяем наличие ключа 'Errors'

    def test_confirm_success(self):
        """
        Тестирует, что подтверждение учетной записи с действительным токеном 
        приводит к ответу 200 и активации учетной записи пользователя.
        """
        user = baker.make(User, email='test@test.com', is_active=False) # создаем тестового пользователя
        token = baker.make(ConfirmEmailToken, user=user) #  создаем тестовый токен
        url = reverse('backend:user-register-confirm') # получаем url эндпоинта ConfirmAccount из пространства имен
        data = {'email': 'test@test.com', 'token': token.key} # пользователь получил на е-маил, правильный токен 
        response = self.client.post(url, data) # и передает его серверному приложению на эндпоинт ConfirmAccount
        user.refresh_from_db() # обновляем объект user
        # После успешного выполнения операции подтверждения email, которая активирует пользователя, 
        # нужно обновить объект пользователя, чтобы отразить изменения, сохраненные в базе данных is_active=True, 
        # так как когда мы создавали тестового пользователя он был is_active=False
        assert response.status_code == 200 # проверяем код ответа
        assert user.is_active is True # проверяем АКТИВАЦИЮ пользователя (пользователь должен быть активирован)


# Тесты для LoginAccount (авторизация пользователя)
@pytest.mark.django_db
class TestLoginAccount(APITestCase):
    def test_login_invalid_credentials(self):
        """
        Тесты, которые показывают, что вход в систему с недействительными учетными данными возвращает ответ 400.
        """
        user = baker.make(User, email='test@test.com',  password='TestPass123!', is_active=True) # создаем пользователя (для авторизации он должен быть активирован)
        user.set_password(user.password) # Хешируем тестовый пароль
        user.save() # и сохраняем его в БД
        url = reverse('backend:user-login') # получаем url эндпоинта TestLoginAccount из пространства имен
        data = {'email': 'test@test.com', 'password': 'WrongPass'} # клиент передает неправильный пароль
        response = self.client.post(url, data) # отправляем запрос на эндпоинт TestLoginAccount
        assert response.status_code == 400 # проверяем код ответа
        assert 'Errors' in response.json() # проверяем наличие ключа 'Errors'

    def test_login_success(self):
        """
        Тесты, которые показывают, что при входе активированного пользователя в систему 
        с действительными учетными данными (e-mail, пароль) серверное приложение возвращает ответ 200 и токен.
        """
        user = baker.make(User, email='test@test.com', password='TestPass123!', is_active=True) # создаем тестового активированного пользователя
        user.set_password(user.password) # Хешируем тестовый пароль
        user.save() # и сохраняем его в БД
        url = reverse('backend:user-login') # получаем url эндпоинта TestLoginAccount из пространства имен
        data = {'email': 'test@test.com', 'password': 'TestPass123!'} # формируем тело запроса клиента с правильными данными
        response = self.client.post(url, data) # и отправляем этот запрос на эндпоинт TestLoginAccount
        assert response.status_code == 200 # проверяем код ответа
        assert 'Token' in response.json() # проверяем наличие ключа 'Token' в ответе пользователю 


# Тесты для PartnerUpdateimport (обновление партнера)
@pytest.mark.django_db
class TestPartnerUpdate:
    @pytest.fixture # декоратор для создания клиента API DRF в тестах (для упрощения написания тестов, вместо self.client) 
    def client(self):
        return APIClient()

    def test_partner_update_permission(self, client):
        # Пользователь не является 'shop'
        user = baker.make(User, type='buyer') # назначаем пользователю тип 'buyer' - покупатель 
                # (он должен быть зарегистрирован (токен), активирован, выбран его тип (buyer или shop) и авторизирован (токен))
        
        client.force_authenticate(user=user) # Принудительная аутентификация пользователя для выполнения запроса.
        # Это позволяет обходить процесс фактической аутентификации, 
        # например, предоставление токена или ввода имени пользователя и пароляна во время теста.
        url = reverse('backend:partner-update')
        response = client.post(url, {}) # пользователь пытается обновить партнера но так как он авторизирован как покупатель, он не может
        assert response.status_code == 403 # и получает ошибку 403
        assert response.json()['Error'] == 'Только для магазинов' # и текст ошибки

    def test_unauthenticated_user(self, client):
        # Незарегистрированный, неактивированный и неавторизированный пользователь (если следовать 'user flow')
        url = reverse('backend:partner-update') 
        response = client.post(url, {}) # отправляем POST-запрос на эндпоинт PartnerUpdate !БЕЗ ТОКЕНА В HEADERS!
        assert response.status_code == 403 # проверяем код ответа
        assert response.json()['Error'] == 'Log in required' # и текст ошибки 'Требуется вход (т.е. аутентификация, активация, авторизация)'

    def test_partner_update_invalid_url(self, mocker, client):
        # Неверный URL указан прайс-листа партнера
        user = baker.make('backend.User', type='shop')
        client.force_authenticate(user=user)

        url = reverse('backend:partner-update')
        data = {'url': 'invalid-url'} # клиент передает неверный URL

        response = client.post(url, data)
        assert response.status_code == 400
        assert 'Error' in response.json()  # Текст ошибки может зависеть от URLValidator (см. views.py)

    def test_partner_update_missing_url(self, client):
        # Ошибка: не указан параметр `url` прайс-листа партнера для загрузки товаров
        user = baker.make('backend.User', type='shop')
        client.force_authenticate(user=user)

        url = reverse('backend:partner-update')
        response = client.post(url, {})
        assert response.status_code == 400
        assert response.json()['Errors'] == 'Не указаны все необходимые аргументы'

    @patch('backend.views.get')  # Заменяем метод `requests.get` с помощью Mock для изоляции теста от реальных HTTP-запросов
    @patch('backend.views.load_yaml')  # Заменяем функцию `load_yaml`, которая парсит YAML-файлы, чтобы вернуть заранее заданные данные
    def test_successful_update(self, mock_load_yaml, mock_get, client):
        # Успешное выполнение обновления прайс-листа
        user = baker.make(User, type='shop') # создаем пользователя с типом 'shop' - он имеет права на обновления прайс-листа
        client.force_authenticate(user=user) # Принудительно аутентифицируем пользователя для выполнения запросов, требующие аутентификации

        # Задаем тестовые mock-данные для теста
        mock_load_yaml.return_value = {
            'shop': 'Test Shop',
            'categories': [{'id': 1, 'name': 'Category 1'}],
            'goods': [
                {
                    'id': 1,
                    'name': 'Test Product',
                    'model': 'Model X',
                    'category': 1,
                    'price': 100,
                    'price_rrc': 150,
                    'quantity': 10,
                    'parameters': {'color': 'red'}
                }
            ]
        } 

        # Задаем мок-ответ для `get`, который имитирует получение содержимого файла
        mock_get.return_value.content = b'mock-content'  # Мокирование данных, которые возвращаются как байтовая строка
        url = reverse('backend:partner-update')
        data = {'url': 'http://example.com/test.yml'} # мокированный URL прайс-листа
        response = client.post(url, data, format='json') # отправляем POST-запрос на эндпоинт PartnerUpdate 
        assert response.status_code == 200 
        assert response.json()['Status'] is True # Проверяем, что в ответе содержится ключ 'Status' со значением True









# Тесты для BasketView
@pytest.mark.django_db
class TestBasketView:
    def test_basket_access_unauthorized(self):
        url = reverse('basket')
        response = client.get(url)
        assert response.status_code == 403

    def test_basket_add_items(self):
        user = baker.make(User)
        client.force_authenticate(user=user)
        product = baker.make(Product)
        shop = baker.make(Shop)
        product_info = baker.make(ProductInfo, product=product, shop=shop)
        
        url = reverse('basket')
        data = {'items': '[{"product_info": 1, "quantity": 2}]'}
        response = client.post(url, data)
        assert response.status_code == 200
        assert response.json()['Status'] is True

# Тесты для OrderView
@pytest.mark.django_db
class TestOrderView:
    def test_order_create(self):
        user = baker.make(User)
        client.force_authenticate(user=user)
        contact = baker.make(Contact, user=user)
        order = baker.make(Order, user=user, state='basket')
        
        url = reverse('order')
        data = {'id': order.id, 'contact': contact.id}
        response = client.post(url, data)
        order.refresh_from_db()
        assert response.status_code == 200
        assert order.state == 'new'
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

# Тесты для RegisterAccount
@pytest.mark.django_db # для работы с базой данных
class TestRegisterAccount(APITestCase):
    def test_register_missing_fields(self):
        """
        Tests that POST to register without any fields results in 400 with errors
        """
        url = reverse('backend:user-register')  # задание url из пространства имен
        response = self.client.post(url, {}) # отправка запроса
        assert response.status_code == 400 # проверка статуса
        assert 'Errors' in response.json() # проверка наличия ключа 'Errors'

    def test_register_invalid_password(self):
        """
        Tests that POST to register with an invalid password results in 400 with errors
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
        assert 'password' in response.json()['Errors'] # проверка наличия ключа 'password'

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


# Тесты для ConfirmAccount
@pytest.mark.django_db
class TestConfirmAccount(APITestCase):
    def test_confirm_invalid_token(self):
        """
        Тестирует, что подтверждение учетной записи с недействительным токеном приводит к ответу 400.
        """
        user = baker.make(User, is_active=False) # создаем пользователя
        token = baker.make(ConfirmEmailToken, user=user) # создаем токен
        url = reverse('backend:user-register-confirm') # создаем url
        data = {'email': user.email, 'token': 'wrong_token'} # передаем неправильный токен
        response = self.client.post(url, data) # отправляем запрос
        assert response.status_code == 400 # проверяем код ответа
        assert 'Errors' in response.json() # проверяем наличие ключа 'Errors'

    def test_confirm_success(self):
        """
        Тестирует, что подтверждение учетной записи с действительным токеном приводит к ответу 200 со значением «Статус»: True и активирует пользователя.
        """
        user = baker.make(User, is_active=False) # создаем пользователя
        token = baker.make(ConfirmEmailToken, user=user) #  создаем токен
        url = reverse('backend:user-register-confirm') # создаем url
        data = {'email': user.email, 'token': token.key} # передаем правильный токен
        response = self.client.post(url, data) # отправляем запрос
        user.refresh_from_db() # обновляем данные пользователя
        assert response.status_code == 200 # проверяем код ответа
        assert user.is_active is True # проверяем АКТИВАЦИЮ пользователя

# Тесты для LoginAccount
@pytest.mark.django_db
class TestLoginAccount(APITestCase):
    def test_login_invalid_credentials(self):
        """
        Тесты, которые показывают, что вход в систему с недействительными учетными данными возвращает ответ 400.
        """
        user = baker.make(User, email='test@test.com', is_active=True) # создаем пользователя (для авторизации он должен быть активирован)
        user.set_password('TestPass123!') # устанавливаем пароль
        user.save() # сохраняем
        url = reverse('backend:user-login') # создаем url
        data = {'email': 'test@test.com', 'password': 'WrongPass'} # передаем неправильный пароль
        response = self.client.post(url, data) # отправляем запрос
        assert response.status_code == 400 # проверяем код ответа
        assert 'Errors' in response.json() # проверяем наличие ключа 'Errors'

    def test_login_success(self):
        """
        Тесты, которые показывают, что вход в систему с действительными учетными данными возвращает ответ 200.
        """
        user = baker.make(User, email='test@test.com', is_active=True)
        user.set_password('TestPass123!')
        user.save()
        url = reverse('backend:user-login')
        data = {'email': 'test@test.com', 'password': 'TestPass123!'}
        response = self.client.post(url, data)
        assert response.status_code == 200 # проверяем код ответа
        assert 'Token' in response.json() # проверяем наличие ключа 'Token'


# Тесты для PartnerUpdateimport pytest
@pytest.mark.django_db
class TestPartnerUpdate:
    @pytest.fixture # декоратор для создания клиента API DRF в тестах (для упрощения написания тестов, вместо self.client) 
    def client(self):
        return APIClient()

    def test_partner_update_permission(self, client):
        # Пользователь не является 'shop'
        user = baker.make('backend.User', type='buyer')  # модель User, тип user
        client.force_authenticate(user=user)

        url = reverse('backend:partner-update')
        response = client.post(url, {})
        assert response.status_code == 403
        assert response.json()['Error'] == 'Только для магазинов'

    def test_unauthenticated_user(self, client):
        # Неаутентифицированный пользователь
        url = reverse('backend:partner-update')
        response = client.post(url, {})
        assert response.status_code == 403
        assert response.json()['Error'] == 'Log in required'

    def test_partner_update_invalid_url(self, mocker, client):
        # Неверный URL указан
        user = baker.make('backend.User', type='shop')
        client.force_authenticate(user=user)

        url = reverse('backend:partner-update')
        data = {'url': 'invalid-url'}

        response = client.post(url, data)
        assert response.status_code == 400
        assert 'Error' in response.json()  # Обратите внимание, что текст ошибки может зависеть от URLValidator
    

    def test_partner_update_missing_url(self, client):
        # Ошибка: не указан параметр `url`
        user = baker.make('backend.User', type='shop')
        client.force_authenticate(user=user)

        url = reverse('backend:partner-update')
        response = client.post(url, {})
        assert response.status_code == 400
        assert response.json()['Errors'] == 'Не указаны все необходимые аргументы'

    @patch('backend.views.get')  # Заменяем метод `requests.get`
    @patch('backend.views.load_yaml')  # Заменяем функцию парсинга YAML
    def test_successful_update(self, mock_load_yaml, mock_get, client):
        # Успешное выполнение обновления прайс-листа
        user = baker.make('backend.User', type='shop')
        client.force_authenticate(user=user)

        # Mock данных для теста
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

        mock_get.return_value.content = b'mock-content'

        url = reverse('backend:partner-update')
        data = {'url': 'http://example.com/test.yml'}

        response = client.post(url, data, format='json')
        assert response.status_code == 200
        # assert response.data['Status'] is True
        assert response.json()['Status'] is True









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
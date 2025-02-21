## Тестирование

Чтобы запустить подготовленные тесты, выполните следующие шаги:

1. Установите необходимые зависимости
```bash
pip install pytest pytest-django model_bakery requests-mock pytest-mock
```
2. Настройте окружение
Создайте файл `pytest.ini` в корне проекта:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = your_project.settings
python_files = tests.py test_*.py *_tests.py
addopts = --reuse-db
```
3. Разместите тесты
Создайте структуру директорий:
```
your_app/
├── tests/
│   ├── __init__.py
│   └── test_api.py  # файл с тестами
```
4. Запуск тестов
Основные команды:
```bash
# Все тесты
pytest your_app/tests/ -v

# Конкретный тестовый класс
pytest your_app/tests/test_api.py::TestRegisterAccount -v

# Конкретный тестовый метод
pytest your_app/tests/test_api.py::TestRegisterAccount::test_register_success -v

# Запись лога
pytest your_app/tests/test_api.py::TestRegisterAccount::test_register_success -v --log-cli-level=INFO
```
5. Пример вывода при успешном запуске
```bash
============================= test session starts ==============================
collected 9 items

your_app/tests/test_api.py::TestRegisterAccount::test_register_missing_fields PASSED
your_app/tests/test_api.py::TestRegisterAccount::test_register_invalid_password PASSED
your_app/tests/test_api.py::TestRegisterAccount::test_register_success PASSED
...
============================== 9 passed in 2.15s ===============================
```
6. Возможные проблемы и решения
Проблема: База данных не создается
Решение: Добавьте флаг при первом запуске:

```bash
pytest --create-db
````
Проблема: Ошибки с миграциями
Решение: Выполните миграции перед тестами:
```bash
python manage.py migrate
```
7. Дополнительные настройки
Для детализации вывода используйте:
```bash
pytest -v          # Подробный вывод
pytest --cov       # Покрытие кода
pytest -x          # Остановка при первой ошибке
pytest --ff        # Запуск сначала проваленных тестов
```
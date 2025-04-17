# Пример API-сервиса для магазина

[Исходная документация по запросам в PostMan](https://documenter.getpostman.com/view/5037826/SVfJUrSc) 

## Разворачиваем проект
более подробно:

https://realpython.com/asynchronous-tasks-with-django-and-celery/
https://stackabuse.com/asynchronous-tasks-in-django-with-redis-and-celery/

### Установка Redis на Windows

- [Загрузите zip-файл Redis](https://github.com/microsoftarchive/redis/releases/tag/win-3.2.100) и распакуйте его в какую-нибудь директорию.
- Найдите файл с именем `redis-server.exe` и дважды щелкните по нему, чтобы запустить сервер в командном окне.
- Аналогично найдите другой файл с именем `redis-cli.exe` и дважды щелкните по нему, чтобы открыть программу в отдельном командном окне.
- В командном окне, запустив клиент CLI, проверьте, может ли клиент взаимодействовать с сервером, выполнив команду, и если все пройдет хорошо , должен быть возвращен pingответ `PONG`

### Установка Redis на Mac OSX / Linux

- [Загрузите файл tarball](https://redis.io/download) Redis и распакуйте его в какой-нибудь каталог.
- Запустите `makefile`, чтобы собрать программу
```bash 
make install
```
- Откройте окно терминала и выполните 
```bash
redis-server
```
- В другом окне терминала запустите клиент CLI
```bash 
redis-cli
```
проверьте, может ли клиент взаимодействовать с сервером, выполнив команду `ping`, и если все пройдет хорошо , должен быть возвращен ответ `PONG`
```bash
127.0.0.1:6379> ping
```

### Установка Redis с помощью docer-compose
Создайте `.yml` файл следующего содержания
```
version: '3.1'

services:

  redis:
    image: redis
    ports:
      - "6379:6379"
```

Запустить сборку
```
docker-compose up -d
```

1. Установка виртуального окружения Python и зависимостей requirements.txt, в том числе и `Celery`

2. Откройте три отдельных окна терминала перейдите в папку в которой находится `manage.py` и запустите почередно:
```bash
(venv) $ python manage.py runserver
$ redis-server # — единственный из трех, который вы можете запустить за пределами своей виртуальной среды
(venv) $ python -m celery -A netology_pd_diplom worker
```

## Разворачиваем проект с помощью Docker и Docker-compose

1. Клонировать приоект

2. Перейти в рабочую дерриктороию

3. Загрузить все переменные сред
```bash
export DEBUG=True
export SECRET_KEY="your_secret_key_here" # Отправил почтой
export ALLOWED_HOSTS=localhost,127.0.0.1 # Или * - доступ с любого адреса
export DB_ENGINE=django.db.backends.sqlite3 
export DB_NAME=db.sqlite3 
export EMAIL_HOST_PASSWORD="your_email_password" # Пароль привязанный к почтовому сервису (Настройки для mail.ru, справка https://help.mail.ru/mail/security/protection/external/) Отправил почтой
```

для PostgreSQl
```bash
export DEBUG=True
export SECRET_KEY="your_secret_key_here"
export ALLOWED_HOSTS=localhost,127.0.0.1
export DB_ENGINE=django.db.backends.postgresql
export DB_NAME="your_postgres_db_name"
export POSTGRES_USER="your_postgres_db_user"
export POSTGRES_PASSWORD="your_postgres_db_pass"
export EMAIL_HOST_PASSWORD="your_email_host_password"
```

Кроме того, если видишь сообщение Compose can now delegate builds to bake for better performance,
можешь включить использование нового инструмента Bake для сборки образов, установив переменную окружения:
```bash
export COMPOSE_BAKE=true
```

5.  Запустить сборку (--build для пересборки)
```bash
docker-compose up -d --build
``` 

---
## Дополнительное задание
> Отказ от django signals, с дальнейшей интеграцией в проект фреймворка Celery для по-настоящему асинхронных задач
Рекомендую начать с использования любой из нижеследующих инструкций.
- https://realpython.com/asynchronous-tasks-with-django-and-celery/

или
- https://stackabuse.com/asynchronous-tasks-in-django-with-redis-and-celery/

> Вижу вы покрыли код тестами, предлагаю добавить красивую кнопку с текущим покрытием у себя в Гитхабе
https://github.com/marketplace/actions/python-coverage

> Опробовать автогенерацию документации Open API в рамках пакета DRF-Spectacular. После внедрения обязательно внимательно просмотрите страницу Swagger. Тут сразу можно будет оценить для себя разницу с Postman и огромный потенциал для плодотворной работы в команде с несколькими разработчиками. P.S. Используйте чаще docstring к классам и функциям
https://drf-spectacular.readthedocs.io/en/latest/readme.html

> Попробовать простой DRF тротлинг, и можно проверить его работу добавление отдельного TestCase
https://www.django-rest-framework.org/api-guide/throttling/

> Добавить возможность авторизации с 1-2 социальных сетей, тут можно ознакомится с такой крутой библиотекой
https://github.com/python-social-auth/social-app-django

> Наверняка пользовались админкой в ходе создания проекта, предлагаю сделать ей мощный тюнинг через эти библиотеки на выбор:
https://github.com/otto-torino/django-baton
https://django-jet-reboot.readthedocs.io/en/latest/

> После добавления Celery можно добавить загрузку аватаров пользователей и картинок товаров с последующей асинхронной обработкой их в фоновом режиме, например создание миниатюр различного размера для быстрой загрузки. Для этого есть множество библиотек на выбор:
https://easy-thumbnails.readthedocs.io/en/latest/
https://django-versatileimagefield.readthedocs.io/en/latest/
https://django-imagekit.readthedocs.io/en/latest/

> Очень часто в коммерческих проектах для перехвата ошибок, которые возникают у пользователей внедряют Sentry или Rollbar. Он позволяет быть в курсе насколько стабильно работает проект и к тому же хранит полные traceback ошибок, так чтобы можно было их исследовать. Будет большой плюс в резюме от наличия знаний по этой технологии. Попробуйте внедрить ее на базовом уровне и создать APIView, который вызывает исключение, что увидеть его в консоли Sentry или RollBar
https://blog.sentry.io/monitoring-performance-and-errors-in-a-django-application-with-sentry/
https://docs.sentry.io/platforms/python/integrations/django/
RollBar
https://docs.rollbar.com/docs/django
https://docs.rollbar.com/docs/celery

> внедрить кэширование запросов к БД с использованием Redis, посмотреть насколько уменьшится время отклика системы. Вот эти библиотеки на выбор могут помочь с кэшированием запросов к БД:
https://github.com/noripyt/django-cachalot
https://github.com/Suor/django-cacheops

> и последнее только по желанию, часто в проектах бывают задачи поиска причин медленной работы запроса. Например, из-за неправильного ORM запроса к БД. Рекомендую ознакомиться с пакетом https://github.com/jazzband/django-silk
проанализировать запросы в Postman и посмотреть какие из них вызывают каскад вторичных запросов, которые перегружают СУБД. Лично у меня вызывает удовлетворение, если ранее запрос выполнялся 400-500 мс, а сейчас за 3-4 мс, после того как я выявил проблему через Silk и оптимизировал запрос. Возможно, и Вам понравится)

---

## **Получить исходный код**

    git config --global user.name "YOUR_USERNAME"
    
    git config --global user.email "your_email_address@example.com"
    
    mkdir ~/my_diplom
    
    cd my_diplom
    
    git clone git@github.com:A-Iskakov/netology_pd_diplom.git
    
    cd netology_pd_diplom
    
    sudo pip3 install  --upgrade pip
    
    sudo pip3 install -r requirements.txt
    
    python3 manage.py makemigrations
     
    python3 manage.py migrate
    
    python3 manage.py createsuperuser    
    
 
## **Проверить работу модулей**
    
    
    python3 manage.py runserver 0.0.0.0:8000


## **Установить СУБД (опционально)**

    sudo nano  /etc/apt/sources.list.d/pgdg.list
    
    ----->
    deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main
    <<----
    
    
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    
    sudo apt-get update
    
    sudo apt-get install postgresql-11 postgresql-server-dev-11
    
    sudo -u postgres psql postgres
    
    create user diplom_user with password 'password';
    
    alter role diplom_user set client_encoding to 'utf8';
    
    alter role diplom_user set default_transaction_isolation to 'read committed';
    
    alter role diplom_user set timezone to 'Europe/Moscow';
    
    create database diplom_db owner mploy;
    alter user mploy createdb;

    
   

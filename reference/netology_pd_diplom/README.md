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

2. Установка виртуального окружения Python и зависимостей requirements.txt, в том числе и `Celery`
3. Откройте три отдельных окна терминала и запустите:
```bash
(venv) $ python manage.py runserver
$ redis-server # — единственная из трех, которую вы можете запустить за пределами своей виртуальной среды
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
5.  Запустить сборку 
```bash
docker-compose up -d --build
``` 

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

    
   

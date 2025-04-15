# Пример API-сервиса для магазина

[Исходная документация по запросам в PostMan](https://documenter.getpostman.com/view/5037826/SVfJUrSc) 

## С помощью Docker и Docker-compose

1. Клонировать приоект
2. Перейти в рабочую дерриктороию
3. Загрузить все переменные сред
```bash
    export DEBUG="True"
    export SECRET_KEY="your_secret_key_here"
    export ALLOWED_HOSTS="localhost"
    export DB_ENGINE="django.db.backends.postgresql"
    export DB_NAME="your_database_name"
    export EMAIL_HOST_PASSWORD="your_email_password"
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

    
   

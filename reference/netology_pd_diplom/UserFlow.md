## Юзер флоу с ссылками на эндпоинты:
*Ниже представлен уточненный юзер флоу с привязкой к эндпоинтам. Данный юзер флоу охватывает полное взаимодействие пользователя с интернет-магазином, включая регистрацию, авторизацию, управление контактами, работу с заказами и управление магазинами, а также события, которые инициируют отправку уведомлений по электронной почте, улучшая пользовательский опыт и обеспечивая ясность в коммуникации.*

---

### 1. **Регистрация пользователя**
- Эндпоинт: **POST `/user/register`**
  - Новый пользователь регистрируется, предоставляя уникальный email, пароль и дополнительные данные о компании. Пользователь может зарегистрироваться как покупатель buyer (по умолчанию) или магазин shop (в административной панеле сервиса).

```bash
curl --location --request POST 'http://localhost:8000/api/v1/user/register' \
--form 'first_name="Константин"' \
--form 'last_name="Фещук"' \
--form 'email="dilmah949dilma@gmail.com"' \
--form 'password="qwer1234A"' \
--form 'company=""' \
--form 'position=""'
```
```bash
{
    "Status": true
}
```
- **Событие:** При создании нового пользователя отправляется e-mail с токеном подтверждения для активации учетной записи.

- Подтверждение email:
  - Эндпоинт: **POST `/user/register/confirm`**
  - Пользователь подтверждает свою почту, передавая в теле запроса токен подтверждения, чтобы активировать учетную запись (`is_active`). При этом токен, в целях безопасности, удаляется из базы данных.

```bash
curl --location --request POST 'http://localhost:8000/api/v1/user/register/confirm' \
--form 'email="dilmah949dilma@gmail.com"' \
--form 'token="c335efb7aef8e3d3f0df5951450"'
```
```bash
{
    "Status": true
}
```

---

### 2. **Авторизация**
- Эндпоинт: **POST `/user/login`**
  - Пользователь вводит логин (email) и пароль для входа в систему. После успешного входа система проверяет активность учетной записи (`is_active`) и формирует токен для аутентификации. Этот токен далее передается в заголовке `Authorization` во всех последующих запросах, чтобы идентифицировать пользователя.

```bash
curl --location --request POST 'http://localhost:8000/api/v1/user/login' \
--form 'email="dilmah949dilma@gmail.com"' \
--form 'password="qwer1234A"'
```
```bash
{
    "Status": true,
    "Token": "e77fbc201870a229252b67a35ed1600e6a60bbd5"
}
```
---

### 3. **Просмотр и редактирование данных пользователя**
- Эндпоинт: **GET, POST `/user/details`**
  - Зарегистрированный пользователь получает информацию о своем профиле и может редактировать ее методом POST.
  
**Просмотр данных пользователя о своем профиле**
Ключ `contacts` содержит список контактных данных пользователя и заполняется после добавления пользователем своего контакта (см. пункт 4)
```bash
curl --location --request GET 'http://localhost:8000/api/v1/user/details' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5'
```
```bash
{
    "id": 24,
    "first_name": "Костя",
    "last_name": "Фещук",
    "email": "dilmah949dilma@gmail.com",
    "company": "",
    "position": "",
    "contacts": [
        {
            "id": 3,
            "city": "Калининград",
            "street": "Бахчисарайска",
            "house": "26",
            "structure": "4",
            "building": "",
            "apartment": "",
            "phone": "89210088233"
        }
    ]
}
```

**Редактирование данных пользователя о своем профиле методом POST**

```bash
curl --location --request POST 'http://localhost:8000/api/v1/user/details' \
--header 'Authorization: Token  e77fbc201870a229252b67a35ed1600e6a60bbd5' \
--form 'first_name="Константин Николаевич"' \
--form 'last_name="Фещук"' \
--form 'email="dilmah949dilma@gmail.com"' \
--form 'password="qwer1234A"' \
--form 'company="mycompany"' \
--form 'position="myposition"'
```
```bash
{
    "Status": true
}
```
---

### 4. **Управление контактами пользователя**
- Эндпоинт: **POST/GET/PUT/DELETE `/user/contact`**
  - Пользователь может добавлять, изменять или удалять контактную информацию (например, адрес и телефон), используемую для выполнения заказов.

**Добавление контактной информации**
```bash
curl --location --request POST 'http://localhost:8000/api/v1/user/contact' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5' \
--form 'city="Калининград"' \
--form 'street="Бахчисарайская"' \
--form 'house="26"' \
--form 'structure="4"' \
--form 'building="123"' \
--form 'apartment="123"' \
--form 'phone="+49564563242"'
```
```bash
{
    "Status": true
}
```

**Просмотр контактной информации**
```bash
curl --location --request GET 'http://localhost:8000/api/v1/user/contact' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5'
```
```bash
[
    {
        "id": 1,
        "city": "Калининград",
        "street": "Бахчисарайская",
        "house": "26",
        "structure": "4",
        "building": "123",
        "apartment": "123",
        "phone": "+49564563242"
    }
]
```

**Удаление контактной информации**
```bash
curl --location --request DELETE 'http://localhost:8000/api/v1/user/contact' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5' \
--form 'items="1,2"'
```
```bash
{
    "Status": true,
    "Удалено объектов": 2
}
```

**Редактирование контактной информации**
```bash
curl --location --request PUT 'http://localhost:8000/api/v1/user/contact' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5' \
--form 'city="Калининград"' \
--form 'street="Бахчисарайска"' \
--form 'house="26"' \
--form 'structure="4"' \
--form 'building=""' \
--form 'apartment=""' \
--form 'id="3"' \
--form 'phone="89210088233"'
```
```bash
{
    "Status": true
}
```
---

### 5. **Работа покупателей**

#### 5.1. **Просмотр магазинов**
- Эндпоинт: **GET `/shops`**
  - Покупатель получает список активных магазинов, готовых к приему заказов (`Shop.state = True`).
```bash
curl --location --request GET 'http://localhost:8000/api/v1/shops'
```
```bash
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Связной",
            "state": true
        }
    ]
}
```
#### 5.2. **Просмотр категорий товаров**
- Эндпоинт: **GET `/categories`**
  - Пользователь видит список категорий товаров, доступных для покупки.
```bash
curl --location --request GET 'http://localhost:8000/api/v1/categories'
```
```bash
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "name": "Телевизоры"
        },
        {
            "id": 224,
            "name": "Смартфоны"
        },
        {
            "id": 15,
            "name": "Аксессуары"
        },
        {
            "id": 1,
            "name": "Flash-накопители"
        }
    ]
}
```
#### 5.3. **Просмотр товаров магазина**
- Эндпоинт: **GET `/products?shop_id=1&category_id=224`**
  - Покупатель видит доступные товары из каталога магазина, включая их характеристики и наличие.
```bash
curl --location --request GET 'http://localhost:8000/api/v1/products?shop_id=1&category_id=224'
```
<details>
<summary>Нажмите, чтобы развернуть</summary>

```bash
[
    {
        "id": 15,
        "model": "apple/iphone/xs-max",
        "product": {
            "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
            "category": "Смартфоны"
        },
        "shop": 1,
        "quantity": 14,
        "price": 110000,
        "price_rrc": 116990,
        "product_parameters": [
            {
                "parameter": "Диагональ (дюйм)",
                "value": "6.5"
            },
            {
                "parameter": "Разрешение (пикс)",
                "value": "2688x1242"
            },
            {
                "parameter": "Встроенная память (Гб)",
                "value": "512"
            },
            {
                "parameter": "Цвет",
                "value": "золотистый"
            }
        ]
    },
    {
        "id": 16,
        "model": "apple/iphone/xr",
        "product": {
            "name": "Смартфон Apple iPhone XR 256GB (красный)",
            "category": "Смартфоны"
        },
        "shop": 1,
        "quantity": 9,
        "price": 65000,
        "price_rrc": 69990,
        "product_parameters": [
            {
                "parameter": "Диагональ (дюйм)",
                "value": "6.1"
            },
            {
                "parameter": "Разрешение (пикс)",
                "value": "1792x828"
            },
            {
                "parameter": "Встроенная память (Гб)",
                "value": "256"
            },
            {
                "parameter": "Цвет",
                "value": "красный"
            }
        ]
    },
    {
        "id": 17,
        "model": "apple/iphone/xr",
        "product": {
            "name": "Смартфон Apple iPhone XR 256GB (черный)",
            "category": "Смартфоны"
        },
        "shop": 1,
        "quantity": 5,
        "price": 65000,
        "price_rrc": 69990,
        "product_parameters": [
            {
                "parameter": "Диагональ (дюйм)",
                "value": "6.1"
            },
            {
                "parameter": "Разрешение (пикс)",
                "value": "1792x828"
            },
            {
                "parameter": "Встроенная память (Гб)",
                "value": "256"
            },
            {
                "parameter": "Цвет",
                "value": "черный"
            }
        ]
    },
    {
        "id": 18,
        "model": "apple/iphone/xr",
        "product": {
            "name": "Смартфон Apple iPhone XR 128GB (синий)",
            "category": "Смартфоны"
        },
        "shop": 1,
        "quantity": 7,
        "price": 60000,
        "price_rrc": 64990,
        "product_parameters": [
            {
                "parameter": "Диагональ (дюйм)",
                "value": "6.1"
            },
            {
                "parameter": "Разрешение (пикс)",
                "value": "1792x828"
            },
            {
                "parameter": "Встроенная память (Гб)",
                "value": "256"
            },
            {
                "parameter": "Цвет",
                "value": "синий"
            }
        ]
    },
    {
        "id": 23,
        "model": "xiaomi/mi-10t-pro",
        "product": {
            "name": "Smartphone Xiaomi Mi 10T Pro 256GB (cosmic black)",
            "category": "Смартфоны"
        },
        "shop": 1,
        "quantity": 6,
        "price": 70000,
        "price_rrc": 74990,
        "product_parameters": [
            {
                "parameter": "Screen Size (inches)",
                "value": "6.67"
            },
            {
                "parameter": "Resolution (pixels)",
                "value": "2400x1080"
            },
            {
                "parameter": "Internal Memory (GB)",
                "value": "256"
            },
            {
                "parameter": "Color",
                "value": "cosmic black"
            }
        ]
    }
]
```
</details>

#### 5.4. **Добавление товаров в корзину. Просмотр и изменение ее содержимого**
- Эндпоинт: **POST/GET/PUT/DELETE `/basket`**
  - Авторизиролванный как пркупатель пользователь может добавлять товары и их количество в корзину, редактировать их количество или удалять товары. На этом этапе создается заказ `Order` с полем `state="basket"` (статус - корзина).
  Также покупатель может просмотреть товары находящиеся в корзине. 

**Добавление товара в корзину**
```bash
curl --location --request POST 'http://localhost:8000/api/v1/basket' \
--header 'Content-Type: application/x-www-form-urlencoded ' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5' \
--form 'items="[
        {
            \"product_info\": 25,
            \"quantity\": 13
        },
        {
            \"product_info\": 26,
            \"quantity\": 12
        }
    ]"'
```

```bash
{
    "Status": true,
    "Создано объектов": 2
}
```


**Просмотр корзины**
```bash
curl --location --request GET 'http://localhost:8000/api/v1/basket' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5'
```

<details>
<summary>Нажмите, чтобы развернуть</summary>

```bash
[
    {
        "id": 1,
        "ordered_items": [
            {
                "id": 3,
                "product_info": {
                    "id": 25,
                    "model": "lg/oled-cx",
                    "product": {
                        "name": "LG OLED CX 55\" 4K UHD Smart TV",
                        "category": "Телевизоры"
                    },
                    "shop": 1,
                    "quantity": 7,
                    "price": 1800,
                    "price_rrc": 1999,
                    "product_parameters": [
                        {
                            "parameter": "Screen Size (inches)",
                            "value": "55"
                        },
                        {
                            "parameter": "Resolution (pixels)",
                            "value": "3840x2160"
                        },
                        {
                            "parameter": "Smart TV",
                            "value": "True"
                        }
                    ]
                },
                "quantity": 13
            },
            {
                "id": 4,
                "product_info": {
                    "id": 26,
                    "model": "sony/bravia-x900h",
                    "product": {
                        "name": "Sony Bravia X900H 75\" 4K UHD Smart TV",
                        "category": "Телевизоры"
                    },
                    "shop": 1,
                    "quantity": 3,
                    "price": 3000,
                    "price_rrc": 3499,
                    "product_parameters": [
                        {
                            "parameter": "Screen Size (inches)",
                            "value": "75"
                        },
                        {
                            "parameter": "Resolution (pixels)",
                            "value": "3840x2160"
                        },
                        {
                            "parameter": "Smart TV",
                            "value": "True"
                        }
                    ]
                },
                "quantity": 12
            }
        ],
        "state": "basket",
        "dt": "2025-02-28T21:05:14.051909Z",
        "total_sum": 59400,
        "contact": null
    }
]
```
</details>

**Удаление выбранных товаров из корзины**
```bash
curl --location --request DELETE 'http://localhost:8000/api/v1/basket' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5' \
--form 'items="1,2"'
```

```bash
{
    "Status": true,
    "Удалено объектов": 2
}
```

**Редактирование количество товаров в корзине**
```bash
curl --location --request PUT 'http://localhost:8000/api/v1/basket' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5' \
--form 'items="[
        {
            \"id\": 5,
            \"quantity\": 3
        },
        {
            \"id\": 6,
            \"quantity\": 1
        }
    ]"'
```

```bash
{
    "Status": true,
    "Обновлено объектов": 2
}
```

#### 5.5. **Оформление заказа**
- Эндпоинт: **POST `/order`**
  - Покупатель отправляет форму с контактными данными (`id` - id заказа и `contact` - id контактной информации). Заказ меняет статус на `state="new"` и становится доступен для обработки магазином.
```bash
curl --location --request POST 'http://localhost:8000/api/v1/order' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: Token e77fbc201870a229252b67a35ed1600e6a60bbd5' \
--form 'id="1"' \
--form 'contact="3"'
```

```bash
{
    "Status": true
}
```
---

### 6. **Работа с заказами**

#### 6.1. **Просмотр своих заказов (покупатель)**
- Эндпоинт: **GET `/order`**
  - Покупатель видит список своих заказов, их статусы (`new`, `confirmed`, `sent`, `delivered`, `canceled`) и детали.

#### 6.2. **Получение заказов (магазин)**
- Эндпоинт: **GET `/partner/orders`**
  - Магазин получает список новых заказов, поступивших от покупателей, для обработки.

#### 6.3. **Обновление состояния заказа**
- Эндпоинт: **PUT `/partner/orders`**
  - Магазин меняет статус заказа на значения `"confirmed"`, `"assembled"`, `"sent"`, `"delivered"` или `"canceled"` в соответствии с этапами его обработки.
- Событие: При изменении состояния заказа отправляется e-mail пользователю с уведомлением о статусе заказа. 

---

### 7. **Управление магазином (для владельцев магазинов)**

#### 7.1. **Обновление товаров и данных магазина**
- Эндпоинт: **POST `/partner/update`**
  - Магазин добавляет или обновляет информацию о своих товарах, ценах и наличии.

#### 7.2. **Изменение статуса магазина**
- Эндпоинт: **PUT `/partner/state`**
  - Владелец магазина может включать или отключать свой магазин, чтобы управлять возможностью принимать новые заказы (`state=True/False`).****

---

### 8. **Сброс пароля**
- Эндпоинты:
  - **POST `/user/password_reset`** — для запроса сброса пароля.
  
```bash
curl --location --request POST 'http://localhost:8000/api/v1/user/password_reset' \
--form 'email="dilmah949dilma@gmail.com"'
```

```bash
{
    "status": "OK"
}
```
  
  - **Событие:** При создании токена сброса пароля отправляется e-mail пользователю с токеном для сброса пароля.****
  
  - **POST `/user/password_reset/confirm`** — для подтверждения сброса и установки нового пароля.

```bash
curl --location --request POST 'http://localhost:8000/api/v1/user/password_reset/confirm' \
--form 'email="dilmah949dilma@gmail.com"' \
--form 'password="qwer1234Anew"' \
--form 'token="adeaf600a9098d0e730e1025576d70a14ac3c6a"'
```

```bash
{
    "status": "OK"
}
```







Юзер флоу описывает взаимодействие пользователя с системой интернет-магазина, построенного на основе моделей выше. Вот шаги:

### 1. **Регистрация пользователя**
   - Пользователь может зарегистрироваться как:
     - **Покупатель (buyer)** — роль по умолчанию.
     - **Магазин (shop)** — с указанием данных о компании.
   - Для регистрации пользователь предоставляет обязательные данные: 
     - `email` (уникальный идентификатор),
     - пароль,
     - опционально `company` и `position` (для магазинов).
   - После регистрации пользователь получает подтверждение email через модель `ConfirmEmailToken`. Этот шаг необходим для активации аккаунта (`is_active`).

### 2. **Авторизация**
   - Пользователь входит в систему, используя свой email и пароль.
   - После входа система проверяет `is_active`, чтобы убедиться, что email был подтверждён.
   - На основе значения поля `type` (`shop` или `buyer`) система предоставляет соответствующий функционал:
     - Покупатель видит список магазинов и продуктов.
     - Магазин может управлять своими товарами и наличием.

### 3. **Работа покупателей:**
   
#### 3.1. **Просмотр магазинов и категорий**
   - Пользователь видит магазины, которые активно принимают заказы (`Shop.state = True`).
   - Для перечисленных магазинов отображаются категории (`Category`) и соответствующие продукты (`Product`).

#### 3.2. **Добавление товаров в корзину (заказ со статусом `basket`)**
   - Покупатель добавляет товар (используя `ProductInfo`) в корзину. На этом этапе создается объект `Order`:
     - Поле `state` равно `"basket"`.
     - Модель `OrderItem` связывает заказ с конкретными товарами (`ProductInfo`) и количеством.
   - Покупатель может управлять своим заказом (изменять количество, удалять позиции) до его оформления.

#### 3.3. **Оформление заказа**
   - Пользователь заполняет контактные данные через модель `Contact` (например, город, улица, телефон).
   - При отправке заказа поле `state` для `Order` меняется на `"new"`. Этот статус означает, что заказ был создан и ожидает подтверждения магазина.

### 4. **Работа магазина**

#### 4.1. **Получение и подтверждение заказа**
   - Магазин получает список заказов, отправленных покупателями (`Order` с `state="new"`) для обработки.
   - После согласования деталей (например, проверки ассортимента, оплаты) магазин устанавливает статус заказа:
     - `"confirmed"` — заказ подтвержден и передан на сборку.
     - `"canceled"` — заказ отменен.

#### 4.2. **Сборка и отправка заказа**
   - Когда заказ готов, поле `state` меняется на:
     - `"assembled"` — заказ собран.
     - `"sent"` — заказ передан службе доставки.

#### 4.3. **Обработка доставки**
   - После доставки покупателю магазин устанавливает статус:
     - `"delivered"` — заказ успешно доставлен.

### 5. **Отслеживание статусов заказа покупателем**
   - Покупатель может в любое время увидеть свои заказы (связь `Order.user`), а также их статусы (`state`), например:
     - Новый,
     - Подтвержден,
     - Отправлен,
     - Доставлен,
     - Отменен.

### 6. **Управление магазином**
   - Владельцы магазинов могут:
     - Изменять товары и их характеристики (через модели `Product`, `ProductInfo`, `ProductParameter`).
     - Добавлять новые товары в каталог.
     - Управлять статусом магазина (`Shop.state`):
       - Включать/отключать возможность получения заказов.

### 7. **Уведомления**
   - После ключевых переходов между статусами (`state`), пользователи получают уведомления:
     - Покупатель получает уведомление об изменении статуса заказа.
     - Магазин уведомляется о новом заказе.

### Пример:
1. Покупатель зарегистрировался и подтвердил email.
2. Зашел в магазин, выбрал товар и добавил в корзину (`basket`).
3. Заполнил контактные данные и оформил заказ (`new`).
4. Магазин подтвердил заказ (`confirmed`), собрал его (`assembled`), отправил (`sent`) и успешно доставил (`delivered`).

Этот юзер флоу позволяет четко организовать взаимодействие пользователей, магазинов и системы для управления электронной коммерцией.





В классе `Shop` поле `state` используется для обозначения статуса получения заказов, что позволяет управлять возможностью или ограничениями на выполнение заказов из данного магазина. 

### Описание поля `state`

- **Имя поля**: `state`
- **Тип данных**: `BooleanField`
- **Значение по умолчанию**: `True` (магазин по умолчанию принимает заказы).

### Возможные значения:

1. **True**:
   - Магазин активно принимает заказы. Это означает, что пользователи могут оформлять покупки, и заказы будут обрабатываться.
  
2. **False**:
   - Магазин временно не принимает заказы. Это может быть использовано в ситуациях, когда магазин закрыт, ведутся работы или другой обстоятельств, из-за которого не могут приниматься заказы.

### Применение поля `state`

Поле `state` может быть полезно для реализации различных бизнес-процессов:

- **Управление доступностью**: Если магазин временно закрыт (например, на ремонт или на время распродажи с изменением ассортимента), это поле может быть установлено в `False`, и все попытки оформить заказ будут отклонены.
- **Уведомления**: Система может уведомлять пользователей о том, что магазин не принимает заказы в данный момент.
- **Логика обработки**: В зависимости от состояния этого поля, можно динамически изменять доступность кнопок и форм для оформления заказа на фронтенде.

Таким образом, поле `state` в модели `Shop` играет важную роль в управлении состоянием магазина и оптимизации взаимодействия клиентов с ним.
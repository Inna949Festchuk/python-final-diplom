# Юзер флоу с ссылками на эндпоинты:
### *Ниже представлен уточненный юзер флоу с привязкой к эндпоинтам. Данный юзер флоу охватывает полное взаимодействие пользователя с интернет-магазином, включая регистрацию, авторизацию, управление контактами, работу с заказами и управление магазинами, а также события, которые инициируют отправку уведомлений по электронной почте, улучшая пользовательский опыт и обеспечивая ясность в коммуникации.*
---

[Документация в Postman](https://www.postman.com/martian-meadow-988006/workspace/my-diplom/collection/24194477-dd78304f-62a3-4f96-b0f3-aacd6094d18e?action=share&creator=24194477)

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
        "contact": null # Заполнить при добавлении контакта
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
  
- Событие: При изменении состояния заказа отправляется e-mail магазину с уведомлением об изменении статуса заказа с сообщением ЭТО NEW!!! >>> "Статус заказа изменен на: Новый" <<< ЭТО NEW!!!.
  
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

```bash
curl --location --request GET 'http://localhost:8000/api/v1/order' \
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
                "id": 5,
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
                "quantity": 3
            },
            {
                "id": 6,
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
                "quantity": 1
            }
        ],
        "state": "new",
        "dt": "2025-02-28T21:05:14.051909Z",
        "total_sum": 8400,
        "contact": {
            "id": 3,
            "city": "Калининград",
            "street": "Бахчисарайска",
            "house": "26",
            "structure": "4",
            "building": "",
            "apartment": "",
            "phone": "89210088233"
        }
    }
]
```
</details>

#### 6.2. **Получение заказов (магазин)**
- Эндпоинт: **GET `/partner/orders`**
  - Магазин получает список новых заказов, поступивших от покупателей, для обработки.

```bash
curl --location --request GET 'http://localhost:8000/api/v1/partner/orders' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: Token 53a4742c02627553d1dbee0268815f72d1c40b5b'
```

<details>
<summary>Нажмите, чтобы развернуть</summary>

```bash
[
    {
        "id": 1,
        "ordered_items": [
            {
                "id": 5,
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
                "quantity": 3
            },
            {
                "id": 6,
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
                "quantity": 1
            }
        ],
        "state": "new",
        "dt": "2025-02-28T21:05:14.051909Z",
        "total_sum": 8400,
        "contact": {
            "id": 3,
            "city": "Калининград",
            "street": "Бахчисарайска",
            "house": "26",
            "structure": "4",
            "building": "",
            "apartment": "",
            "phone": "89210088233"
        }
    }
]
```
</details>

#### 6.3. **Обновление состояния заказа** (NEW!)
- Эндпоинт: **POST `/partner/orders`**
  - Магазин меняет статус заказа на значения `STATE_CHOICES` соответствующие `"confirmed"`, `"assembled"`, `"sent"`, `"delivered"` или `"canceled"` в соответствии с этапами его обработки.
  
```bash
curl --location --request POST 'http://localhost:8000/api/v1/partner/orders' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: Token 53a4742c02627553d1dbee0268815f72d1c40b5b' \
--form 'id="1"' \  # номер заказа
--form 'state="confirmed"' # статус заказа из STATE_CHOICES
```

```bash
{
    "Status": true
}
```

- Событие: При изменении состояния заказа отправляется e-mail пользователю с уведомлением об измененном статусе заказа. 
Статус заказа обязательно выбирается из `STATE_CHOICES` и из запроса интегрируется в тело письма (<<< ЭТО NEW!)

---

### 7. **Управление магазином (для владельцев магазинов)**

#### 7.1. **Обновление товаров и данных магазина**
- Эндпоинт: **POST `/partner/update`**
  - Магазин добавляет или обновляет информацию о своих товарах, ценах и наличии.

```bash
curl --location --request POST 'http://localhost:8000/api/v1/partner/update' \
--header 'Authorization: Token 53a4742c02627553d1dbee0268815f72d1c40b5b' \
--form 'url="https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"' # это адрес прайса поставщика товаров
```

```bash
{
    "Status": true
}
```

#### 7.2. **Изменение статуса магазина**
- Эндпоинт: **GET, POST `/partner/state`**
  - Владелец магазина может открывать или закрывать свой магазин, чтобы управлять возможностью принимать новые заказы (`state=True/False`).

**Просмотреть статус магазина**

```bash
curl --location --request GET 'http://localhost:8000/api/v1/partner/state' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: Token 53a4742c02627553d1dbee0268815f72d1c40b5b'
```

```bash
{
    "id": 1,
    "name": "Связной",
    "state": true
}
```
**Изменить (открыть/закрыть) статус магазина**

```bash
curl --location --request POST 'http://localhost:8000/api/v1/partner/state' \
--header 'Authorization: Token 53a4742c02627553d1dbee0268815f72d1c40b5b' \
--form 'state="off"' # Или state="on"
```

```bash
{
    "Status": true
}
```

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


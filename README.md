# PyDomosed - API-wrapper для мини-приложений Домосед и Гонки

Домосед (приложение закрыто):
- [Документация API](https://vk.com/@domosedapp-domosed-api)    
- [Мини-приложение](https://vk.com/app7594692)

Гонки:
- [Документация API](https://vk.com/@happyoffice-api)    
- [Мини-приложение](https://vk.com/app7679912)


## Содержание:

- [Содержание (вы находитесь здесь)](#содержание)
- [Базовое использование](#базовое-использование)
- [Установка](#установка)
- [Запросы к API](#запросы-к-api)
- [Подписка на переводы](#подписка-на-переводы)


## Базовое использование

Чтобы использовать API, необходимо создать объект сессии (`Session`)
На примере ниже создаётся event loop () и создаётся сессия и выводится ответ метода `merchants.getInfo`.    
`merchants.getInfo` здесь и далее приведен для примера.

```python
from pydomosed import Session
import asyncio

token = "youraccesstoken"

async def main():
    async with Session(token) as domosed:
        info = await domosed.merchants.getInfo() # Возвращает объект Response
        print(info)
        

asyncio.run(main())
```

### Использование API Гонок

Чтобы использовать API Гонок, замените `Session.base_url` на `Session.api_urls["race"]`:

```python
from pydomosed import Session
import asyncio

token = "youraccesstoken"
Session.base_url = Session.api_urls["race"]

async def main():
    async with Session(token) as raceapi:
        info = await raceapi.merchants.get() # Возвращает объект Response
        print(info)
        

asyncio.run(main())
```

## Установка

- Склонируйте репозиторий и запустите `setup.py`

или воспользуйтесь pip:

- `pip install pydomosed`


## Запросы к API

Все запросы осуществляются через объект сессии. Для удобства и читабельности вашего кода, можно использовать несколько равнозначных способов выполнить запрос:    
(`session` в данных примерах - объект класса `pydomosed.base.Session`)

```python
await session.request("merchants.getInfo", **params)
await session("merchants.getInfo", **params)
await session.merchants.getInfo(**params)
```

Эти способы не различаются внутренне (во всех случаях используется `session.request`) и возвращают объект `Response`.


### pydomosed.base.Response

Класс, предназначенный для хранения информации об ответе. Возвращается при любом запросе к API и содержит следующие атрибуты:

- `data`: Словарь ответа, каким его вернул API
- `success`: True или False, в зависимости от успешности запроса
- `msg`: содержимое `.data["response"]["msg"]`, если запрос был успешен, иначе `None` *(неактуально для приложения Гонки)*
- `error_msg`: сообщение об ошибке, если запрос не был успешен, иначе `None`
- `error_code`: код ошибки, если запрос не был успешен, иначе `None`
- `request_info`: словарь:

```python
{
    "method": "merchants.getInfo",
    "params": {
        "access_token": "some_token",
        ...
    },
    "base_url": "URL, использовавшийся в запросе"
}
```


## Подписка на переводы

Для подписки на переводы необходимо импортировать класс `pydomosed.hooks.Hook`.    
Расширим пример выше, чтобы выводить все события переводов.

```python
from pydomosed import Session, Hook
import asyncio

token = "youraccesstoken"

async def main():
    async with Session(token) as domosed:
        domohook = Hook(domosed, url="http://your.doma.in", port=8080)

        await domohook.start(
            # Задаём функцию, которая будет вызываться на каждое событие. Здесь - вывод всех событий в консоль.
            callback=lambda data: print(data) 
        )

        info = await domosed.merchants.getInfo() # Возвращает объект Response
        print(info)
        

asyncio.run(main())
```

### Использование подписки для Гонок

Чтобы использовать подписку на переводы c API Гонок, замените `Hook.method` на `"webhooks.create"`:

```python
from pydomosed import Session, Hook
import asyncio

token = "youraccesstoken"
Session.base_url = Session.api_urls["race"]
Hook.method = "webhooks.create"

async def main():
    async with Session(token) as raceapi:
        racehook = Hook(domosed, url="http://your.doma.in", port=8080)

        await racehook.start(
            # Задаём функцию, которая будет вызываться на каждое событие. Здесь - вывод всех событий в консоль.
            callback=lambda data: print(data) 
        )
        info = await raceapi.merchants.get() # Возвращает объект Response
        print(info)
        

asyncio.run(main())
```

Класс `pydomosed.hooks.Hook` принимает три обязательных параметра: 
- `session`: объект сессии
- `url`: URL вашего сервера
- `port`: порт

Подписка запускается с помощью `await hook.start(callback)`, где `callback` - функция, в которую первым аргументом передаются события по мере поступления.
Если необходимо остановить подписку до завершения работы всего приложения, можно использовать метод `hook.stop()`

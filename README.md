# PyDomosed - API-wrapper для мини-приложения Домосед

[Документация API](https://vk.com/@domosedapp-domosed-api)    
[Мини-приложение](https://vk.com/app7594692)

## Содержание:

- [Содержание (вы находитесь здесь)](#содержание)
- [Базовое использование](#базовое-использование)
- [Установка](#установка)
- [Запросы к API](#запросы-к-api)
- [Подписка на переводы](#подписка-на-переводы)


## Базовое использование

Чтобы использовать API Домоседа, необходимо создать объект сессии (`Session`)
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
        

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
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
- `msg`: содержимое `.data["response"]["msg"]`, если запрос был успешен, иначе `None`
- `error_msg`: содержимое `.data["error"]["error_msg"]`, если запрос не был успешен, иначе `None`
- `error_code`: содержимое `.data["error"]["error_code"]`, если запрос не был успешен, иначе `None`
- `request_info`: словарь:

```python
{
    "method": "merchants.getInfo",
    "params": {
        "access_token": "some_token",
        ...
    }
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
        

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever() # Чтобы скрипт не завершил работу раньше времени, запускаем бесконечный event loop
```

Класс `pydomosed.hooks.Hook` принимает три обязательных параметра: 
- `session`: объект сессии
- `url`: URL вашего сервера
- `port`: порт

Подписка запускается с помощью `await hook.start(callback)`, где `callback` - функция, в которую первым аргументом передаются события по мере поступления.
Если необходимо остановить подписку до завершения работы всего приложения, можно использовать метод `hook.stop()`

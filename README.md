# MyBybit
MyBybit - это утилитарная библиотека для работы с биржей Bybit.

## Общая информация
### Возможности
1. Асинхронное взаимодействие с биржей.
2. Подключение прокси.
3. Логирование результатов.
4. Работа с публичными данными (получение цен активов).
5. Работа с Unified Trading аккаунтом (Выставление ордеров).

### Методы
1. `is_connected` - проверка подключения к аккаунту Bybit.
2. `make_market_order` - выставление рыночного ордера.
3. `check_order` - получение информации об ордере. 
4. `get_tickers_info` - получение информации об одном или всех тикерах.
5. `get_wallet_balance` - получение баланса Unified Trading аккаунта.
6. `get_coins_info` - получение информации об одной или нескольких монетах. 
7. `get_klines` - получение информации о свечах по выбранному активу.
8. `get_loaded_trades` - получение информации о проведенных сделках.

### Особенности
Почти все методы класса возвращают кортежи с целым числом в качестве первого элемента, где:
- `0`: статус успеха (успешное завершение метода; второй элемент кортежа содержит результат)
- `-1`: статус ошибки (неуспешное завершение метода; второй элемент кортежа содержит ошибку)

## Примеры
### Импорт библиотек
Перед началом импортируем библиотеку `asyncio` для запуска асинхронных функций и сам класс `MyBybit`.
```python
import asyncio
from my_bybit import MyBybit
```

### Создание экземпляра класса `MyBybit`
Создаем экземпляр класса `MyBybit` с обязательным параметрами `api_key`, `secret_key` и опциональным параметром `asynchrony`. Подробнее о параметрах — в комментариях конструктора класса `MyBybit`. 
```python
my_bybit = MyBybit(
    api_key='YOUR-API-KEY',
    secret_key='YOUR-SECRET-KEY',
    asynchrony=True,
)
```

### Пример использования метода `is_connected`
Метод `is_connected` проверяет подключение к аккаунту Bybit. Метод присылает (0, True), если подключение успешное, и (-1, Exception("...")), если нет.
```python
async def example_00():
    status, result = await my_bybit.is_connected()
    if status == 0:
        print(f'00 | Is connected: {result}')
    else:
        print(f'00 | Error while getting price: {result}')
```

### Пример использования метода `get_wallet_balance`
Метод `get_wallet_balance` проверяет баланс определенного актива на Unified Trading аккаунте, если указать параметр `ticker`. Если параметр не будет указан, метод вернет балансы всех доступных активов.
```python
async def example_01():
    status, result = await my_bybit.get_wallet_balance(ticker='BTC')
    if status == 0:
        print(f'01 | Balance info: {result}')
    else:
        print(f'01 | Error while getting price: {result}')

asyncio.run(example_01())
```

### Пример использования метода `make_market_order`
Метод `make_market_order` выставляет спотовый ордер на покупку/продажу по рыночной цене.
```python
async def example_02():
    status, result = await my_bybit.make_market_order(
        symbol='BTCUSDT',
        side='Buy',  # 'Sell'
        qty=1,
    )
    if status == 0:
        print(f'02 | Order info: {result}')
    else:
        print(f'02 | Error while making the order: {result}')

asyncio.run(example_02())
```

### Пример использования метода `get_tickers_info`
Метод `get_tickers_info` получает информацию о тикерах. (Например: шаг цены, максимальный/минимальный размер ордера, параметры риска и т.д.).
```python
async def example_03():
    status, result = await my_bybit.get_tickers_info('BTCUSDT')
    if status == 0:
        print(f'03 | Ticker info: {result}')
    else:
        print(f'03 | Error while getting price: {result}')

asyncio.run(example_03())
```

### Пример использования метода `get_klines`
Метод `get_klines` получает исторические данные по свечам для заданной торговой пары и временного интервала.

```python
async def example_04():
    status, result = await my_bybit.get_klines(
        symbol='ETHUSDT',
        timeframe='1d',
        limit=200,
    )
    if status == 0:
        print(f'04 | Price: {result}')
    else:
        print(f'04 | Error while getting price: {result}')
```

### Пример использования метода `get_loaded_trades`
Метод `get_loaded_trades` получает данные о выполненных ордерах пользователя для заданной торговой пары и временного интервала (не больше 7 дней!).
```python
async def example_05():
    status, result = await my_bybit.get_loaded_trades(symbol='TONUSDT')
    if status == 0:
        print(f'05 | Price: {result}')
    else:
        print(f'05 | Error while getting price: {result}')
        
asyncio.run(example_05())
```

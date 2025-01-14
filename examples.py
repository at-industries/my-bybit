import asyncio
from my_bybit import MyBybit


my_bybit = MyBybit(
    api_key='YOUR_API_KEY',
    secret_key='YOUR_SECRET_KEY',
    asynchrony=True,
)


async def example_00():
    status, result = await my_bybit.is_connected()
    if status == 0:
        print(f'00 | Is connected: {result}')
    else:
        print(f'00 | Error while getting price: {result}')

# asyncio.run(example_00())


async def example_01():
    status, result = await my_bybit.get_wallet_balance(ticker='BTC')
    if status == 0:
        print(f'01 | Balance info: {result}')
    else:
        print(f'01 | Error while getting price: {result}')


# asyncio.run(example_01())


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

# asyncio.run(example_02())


async def example_03():
    status, result = await my_bybit.get_tickers_info('BTCUSDT')
    if status == 0:
        print(f'03 | Ticker info: {result}')
    else:
        print(f'03 | Error while getting price: {result}')

# asyncio.run(example_03())


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

# asyncio.run(example_04())


async def example_05():
    status, result = await my_bybit.get_trade_history(symbol='TONUSDT')
    if status == 0:
        print(f'05 | Price: {result}')
    else:
        print(f'05 | Error while getting price: {result}')

# asyncio.run(example_05())

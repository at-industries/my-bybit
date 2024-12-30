from logging import Logger
from typing import Optional, Union, Tuple

from httpx import Client, AsyncClient, Response

import inspect
import hmac
import time
import hashlib
import httpx

from .utils import afh

from .constants import RECV_WINDOW


class MyBybit:
    name = 'Bybit'
    host = 'https://api.bybit.com'

    def __init__(
            self,
            api_key: Optional[str] = None,
            secret_key: Optional[str] = None,
            proxy: Optional[str] = None,
            logger: Optional[Logger] = None,
            asynchrony: Optional[bool] = False,
    ):
        self._api_key = api_key
        self._secret_key = secret_key
        self._proxy = proxy
        self._logger = logger
        self._asynchrony = asynchrony
        self._httpx_client = self._get_httpx_client()

    async def get_balance(self, coin: str):
        """
        https://api.bybit.com/v5/account/wallet-balance?accountType=UNIFIED&coin={coin}
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/account/wallet-balance'
        method = 'GET'
        body = f'accountType=UNIFIED&coin={coin}'
        try:
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )

            if response.status_code == 200:
                return 0, dict(response.json())
            else:
                json = response.json()
                if True:
                    pass
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_tickers(self,):
        """
        https://api.bybit.com/v5/market/instruments-info?category=spot
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/market/instruments-info'
        method = 'GET'
        body = 'category=spot'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            if response.json()['retCode'] == 0:
                data = response.json()['result']['list']
                tickers = set()
                for coin in data:
                    tickers.add(str(coin['baseCoin']))
                return 0, list(tickers)
            else:
                return -1, Exception(f'{log_process} | {response.json()["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_instrument_info(self, base_currency, quote_currency):
        """
        https://api.bybit.com
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/market/instruments-info'
        method = 'GET'
        body = f'category=spot&symbol={base_currency + quote_currency}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)

            if response.json()['retCode'] == 0:
                data = response.json()['result']['list']
                if len(data) != 0:
                    asset = data[0]
                    instrument_info = {
                        'symbol': str(asset['symbol']),
                        'status': str(asset['status']),
                        'baseCoin': str(asset['baseCoin']),
                        'quoteCoin': str(asset['quoteCoin']),
                        'innovation': float(asset['innovation']),
                        'basePrecision': float(asset['lotSizeFilter']['basePrecision']),
                        'quotePrecision': float(asset['lotSizeFilter']['quotePrecision']),
                        'minOrderQty': float(asset['lotSizeFilter']['minOrderQty']),
                        'maxOrderQty': float(asset['lotSizeFilter']['maxOrderQty']),
                        'minOrderAmt': float(asset['lotSizeFilter']['minOrderAmt']),
                        'maxOrderAmt': float(asset['lotSizeFilter']['maxOrderAmt']),
                        'tickSize': float(asset['priceFilter']['tickSize']),
                    }
                    return 0, instrument_info
                else:
                    return -1, Exception(f'{log_process} | {data}')
            else:
                return -1, Exception(f'{log_process} | {response.json()["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_wallet_balance(self, currency):
        """
        https://api.bybit.com
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/account/wallet-balance'
        method = 'GET'
        body = f'accountType=UNIFIED&coin={currency}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)

            if response.json()['retCode'] == 0:
                wallet_balance = response.json()['result']['list'][0]['coin'][0]['walletBalance']
                wallet_balance = round(float(wallet_balance), 2)
                return 0, wallet_balance
            else:
                return -1, Exception(f'{log_process} | {response.json()["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def place_market_order(self, base_currency, quote_currency, side, amt):
        """
        https://api.bybit.com
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/order/create'
        method = 'POST'
        body = '{"category":"spot","symbol":"'+(base_currency+quote_currency)+'","side":"'+side+'","orderType":"Market","qty":"'+str(amt)+'"}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)

            if response.json()['retCode'] == 0:
                orderId = response.json()['result']['orderId']
                return 0, orderId
            else:
                return -1, Exception(f'{log_process} | {response.json()["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_order_info(self, orderId: int):
        """
        https://api.bybit.com
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/order/history'
        method = 'GET'
        body = f'category=spot&orderId={orderId}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)

            if response.json()['retCode'] == 0:
                order_dict = response.json()['result']['list'][0]
                order_status = order_dict['orderStatus']
                if order_status not in ['Filled', 'PartiallyFilled', 'PartiallyFilledCanceled']:
                    return -2, 'Not executed'
                else:
                    symbol, side, orderType = order_dict['symbol'], order_dict['side'], order_dict['orderType']
                    orderLinkId, timestamp, price = order_dict['orderLinkId'], order_dict['updatedTime'], float(order_dict['avgPrice'])

                    endpoint = '/v5/execution/list'
                    method = 'GET'
                    body = f'category=spot&orderId={orderId}'
                    try:
                        response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
                        executions_list = response.json()['result']['list']
                        amt, qty, fee = 0.0, 0.0, 0.0

                        for execution_dict in executions_list:
                            qty += float(execution_dict['execQty'])
                            fee += float(execution_dict['execFee'])
                        if side == 'Buy':
                            amt = float(price * qty)
                            qty -= fee
                        else:
                            amt = float(price * qty)
                            amt -= fee

                        order_dict = {
                            'symbol': symbol, 'side': side, 'orderType': orderType, 'orderId': orderId, 'orderLinkId': orderLinkId,
                            'price': price, 'amount': amt, 'quantity': qty, 'fee': fee, 'timestamp': timestamp,
                        }
                        return 0, order_dict
                    except Exception as e:
                        return -1, Exception(f'{log_process} | {e}')
            else:
                return -1, Exception(f'{log_process} | {response.json()["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_last_coin_info(self, base_currency, quote_currency):
        """
        https://api.bybit.com
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/market/tickers'
        method = 'GET'
        body = f'category=spot&symbol={base_currency + quote_currency}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)

            if response.json()['retCode'] == 0:
                ticker_dict = response.json()['result']['list'][0]
                last_coin_info = {
                    'lastPrice': float(ticker_dict['lastPrice']),
                    'ask1Price': float(ticker_dict['ask1Price']),
                    'bid1Price': float(ticker_dict['bid1Price']),
                    'ask1Size': float(ticker_dict['ask1Size']),
                    'bid1Size': float(ticker_dict['bid1Size']),
                }
                return 0, last_coin_info
            else:
                return -1, Exception(f'{log_process} | {response.json()["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    # async def get_df_klines(self, base_currency, quote_currency, timeframe, limit):
    #     endpoint = '/v5/market/kline'
    #     method = 'GET'
    #     body = f'category=spot&symbol={base_currency + quote_currency}&interval={TF_TO_INTERVAL[timeframe]}&limit={limit}'
    #     try:
    #         response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
#
    #         dataframe = pd.DataFrame(response.json()['result']['list']).iloc[:, :6]
    #         dataframe.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    #         float_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    #         dataframe['Date'] = pd.to_datetime(dataframe['Date'].astype(int), unit='ms')
    #         dataframe[float_columns] = dataframe[float_columns].astype(float)
    #         return dataframe
    #     except Exception as E:
    #         return pd.DataFrame()

    async def get_last_prices(self,):
        """
        https://api.bybit.com
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/market/tickers'
        method = 'GET'
        body = f'category=spot'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)

            if response.json()['retCode'] == 0:
                coins_list = response.json()['result']['list']
                coins_dict = {}
                for coin_dict in coins_list:
                    coins_dict[coin_dict['symbol']] = float(coin_dict['lastPrice'])
                return 0, coins_dict
            else:
                return -1, Exception(f'{log_process} | {response.json()["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_loaded_trades(self, base_currency, quote_currency, startTime, endTime):
        """
        https://api.bybit.com
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/execution/list'
        method = 'GET'
        body = f'category=spot&symbol={base_currency + quote_currency}&startTime={startTime}&endTime={endTime}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)

            if response.json()['retCode'] == 0:
                loaded_orders_list = response.json()['result']['list']
                loaded_orders_dict, loaded_trades_dict = {}, {}

                for trade_dict in loaded_orders_list:
                    orderId = trade_dict['orderId']
                    if orderId not in loaded_orders_dict:
                        loaded_orders_dict[orderId] = [trade_dict]
                    else:
                        loaded_orders_dict[orderId].append(trade_dict)

                for orderId in loaded_orders_dict:
                    price, amt, qty, fee = 0.0, 0.0, 0.0, 0.0
                    first_trade = loaded_orders_dict[orderId][0]
                    price = float(first_trade['execPrice'])
                    side, orderType, orderLinkId, timestamp = first_trade['side'], first_trade['orderType'], first_trade['orderLinkId'], first_trade['execTime']

                    for order_dict in loaded_orders_dict[orderId]:
                        qty += float(order_dict['execQty'])
                        fee += float(order_dict['execFee'])
                    if side == 'Buy':
                        amt = float(price * qty)
                        qty -= fee
                    else:
                        amt = float(price * qty)
                        amt -= fee

                    order_dict = {
                        'symbol': (base_currency + quote_currency), 'side': side, 'orderType': orderType, 'orderId': orderId, 'orderLinkId': orderLinkId,
                        'price': price, 'amount': amt, 'quantity': qty, 'fee': fee, 'timestamp': timestamp,
                    }
                    loaded_trades_dict[orderId] = order_dict
                return 0, loaded_trades_dict
            else:
                return -1, Exception(f'{log_process} | {response.json()["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    def _get_httpx_client(self, ) -> Union[Client, AsyncClient]:
        if self._asynchrony:
            httpx_client = httpx.AsyncClient(proxy=self.proxy)
        else:
            httpx_client = httpx.Client(proxy=self.proxy)
        return httpx_client

    async def _httpx_request(self, method: str, endpoint: str, body: Union[str, dict]) -> Response:
        timestamp = self.time
        signature = self._get_signature(timestamp, body)
        if body != '':
            print(body)
            print('body is not none')
            body = '?' + body
        headers = {
            'X-BAPI-SIGN': signature,
            'X-BAPI-API-KEY': self._api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': RECV_WINDOW,
            'Content-Type': 'application/json',
        }
        print('headers:', headers)
        if isinstance(body, str):
            print(f'method: {method}')
            print(f'url: {self.host + endpoint + body}')
            print(f'headers: {headers}')
            response = await afh(
                self._httpx_client.request, self._asynchrony,
                method=method, url=(self.host + endpoint + body), headers=headers,
            )
        else:
            response = await afh(
                self._httpx_client.request, self._asynchrony,
                method=method, url=(self.host + endpoint), headers=headers, json=body,
            )
        print(self.host + endpoint + body)
        print(response)
        self._log_debug(response.json())
        return response

    def _get_signature(self, timestamp, body):
        message = str(timestamp) + str(self._api_key) + RECV_WINDOW + body
        hsh = hmac.new(bytes(self._secret_key, "utf-8"), message.encode("utf-8"), hashlib.sha256)
        signature = hsh.hexdigest()
        print(f'return Signature: {signature}')
        return signature

    def _log_debug(self, message: str) -> None:
        if self._logger is not None:
            self._logger.debug(f'{self.name} | {message}')

    @property
    def time(self, ) -> str:
        current_time = round(time.time() * 1000)
        return str(current_time)

    @property
    def proxy(self, ) -> Optional[str]:
        return f'http://{self._proxy}' if self._proxy else None

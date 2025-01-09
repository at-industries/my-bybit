from logging import Logger
from typing import Optional, Union, Tuple
from httpx import Client, AsyncClient, Response

import inspect
import hmac
import time
import hashlib
import httpx

from .utils import afh, tf_to_interval
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
        """
        MyBybit is a convenient library for interacting with the Bybit API.
        For more details about Bybit API, refer to the Bybit Documentation: https://bybit-exchange.github.io/docs/v5/intro

        Almost all class methods (except utility functions) return tuples, with an integer status as the first element:
        - `0`: Success status (indicates the method completed successfully; the second element in the tuple contains the result)
        - `-1`: Error status (indicates the method failed; the second element in the tuple contains an error message)

        :param api_key: API Key (generated on the Bybit website).
        :param secret_key: Secret Key (generated on the Bybit website).
        :param proxy: HTTP/HTTPS proxy (e.g., user12345:abcdef@12.345.67.890:1234).
        :param logger: Logger object (used to log received responses).
        :param asynchrony: Enables asynchronous operations.
        """
        self._api_key = api_key
        self._secret_key = secret_key
        self._proxy = proxy
        self._logger = logger
        self._asynchrony = asynchrony
        self._httpx_client = self._get_httpx_client()

    async def is_connected(self) -> Tuple[int, Union[bool, Exception]]:
        """
        Checks the connection to the account. (using get_wallet_balance endpoint to check connection)
        Endpoint: https://api.bybit.com/v5/account/wallet-balance?accountType=UNIFIED&coin=BTC
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/account/wallet-balance'
        method = 'GET'
        body = f'accountType=UNIFIED&coin=BTC'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            json = response.json()
            if response.status_code == 200:
                if json['result']:
                    return 0, json['result']
                else:
                    return -1, json['retMsg']
            else:
                return -1, Exception(f'{log_process} | {json["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_tickers_info(self, symbol: Optional[str] = None) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets the information about specific ticker or for all tickers.
        Endpoint: https://api.bybit.com/v5/market/instruments-info
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/market/instruments-info'
        method = 'GET'
        body = 'category=spot'
        if symbol is not None:
            body += f'&symbol={symbol}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            json = response.json()
            if response.status_code == 200:
                if json['result']:
                    return 0, json['result']
                else:
                    return -1, json['retMsg']
            else:
                return -1, Exception(f'{log_process} | {json["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_wallet_balance(self, coin: Optional[str] = None) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets the balance of the unified trading account for a specific coin or for all coins.
        Endpoint: https://bybit-exchange.github.io/docs/v5/account/wallet-balance
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/account/wallet-balance'
        method = 'GET'
        body = f'accountType=UNIFIED'
        if coin is not None:
            body += f'&coin={coin}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            json = response.json()
            if response.status_code == 200:
                if json['result']:
                    return 0, json['result']
                else:
                    return -1, json['retMsg']
            else:
                return -1, Exception(f'{log_process} | {json["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def make_market_order(self, symbol: str, side: str, qty: float) -> Tuple[int, Union[dict, Exception]]:
        """
        Creates a market order for a specified trading symbol. Here's a breakdown of its functionality:
        Endpoint: https://bybit-exchange.github.io/docs/v5/order/create-order
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/order/create'
        method = 'POST'
        body = '{' + f'"category": "spot", "symbol": "{symbol}", "side": "{side}", "orderType": "Market", "qty": "{str(qty)}"' + '}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            json = response.json()
            if response.status_code == 200:
                if json['result']:
                    return 0, json['result']
                else:
                    return -1, json['retMsg']
            else:
                return -1, Exception(f'{log_process} | {json["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def check_order(self, order_id: str) -> Tuple[int, Union[dict, Exception]]:
        """
        Creates a market order for a specified trading symbol. Here's a breakdown of its functionality:
        Endpoint: https://bybit-exchange.github.io/docs/v5/order/order-list
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/order/history'
        method = 'GET'
        body = f'category=spot&orderId={order_id}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            json = response.json()
            if response.status_code == 200:
                if json['result']:
                    return 0, json['result']
                else:
                    return -1, json['retMsg']
            else:
                return -1, Exception(f'{log_process} | {json["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_coins_info(self, symbol: Optional[str] = None) -> Tuple[int, Union[dict, Exception]]:
        """
        Query for the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours.
        Endpoint: https://bybit-exchange.github.io/docs/v5/market/tickers
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/market/tickers'
        method = 'GET'
        body = f'category=spot'
        if symbol is not None:
            body += f'&symbol={symbol}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            json = response.json()
            if response.status_code == 200:
                if json['result']:
                    return 0, json['result']
                else:
                    return -1, json['retMsg']
            else:
                return -1, Exception(f'{log_process} | {json["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_klines(self, symbol: str, timeframe: str, limit: Optional[str] = 200) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets query for historical klines. Charts are returned in groups based on the requested interval.
        Endpoint: https://bybit-exchange.github.io/docs/v5/market/kline
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/market/kline'
        method = 'GET'
        try:
            body = f'category=spot&symbol={symbol}&interval={tf_to_interval[timeframe]}&limit={limit}'
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            json = response.json()
            if response.status_code == 200:
                if json['result']:
                    return 0, json['result']
                else:
                    return -1, json['retMsg']
            else:
                return -1, Exception(f'{log_process} | {json["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_loaded_trades(self, symbol: str, start_time: Optional[int], end_time: Optional[int]) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets query users' execution records.
        Endpoint: https://bybit-exchange.github.io/docs/v5/order/execution
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        endpoint = '/v5/execution/list'
        method = 'GET'
        body = f'category=spot&symbol={symbol}'
        if start_time is not None:
            body += f'&startTime={start_time}'
        if end_time is not None:
            body += f'&endTime={end_time}'
        try:
            response = await self._httpx_request(endpoint=endpoint, method=method, body=body)
            json = response.json()
            if response.status_code == 200:
                if json['result']:
                    return 0, json['result']
                else:
                    return -1, json['retMsg']
            else:
                return -1, Exception(f'{log_process} | {json["retMsg"]}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def _httpx_request(self, method: str, endpoint: str, body: Union[str, dict]) -> Response:
        timestamp = self.time
        signature = self._get_signature(timestamp=timestamp, body=body)
        headers = {
            'X-BAPI-SIGN': signature,
            'X-BAPI-API-KEY': self._api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': RECV_WINDOW,
            'Content-Type': 'application/json',
        }
        if method == 'GET':
            response = await afh(
                self._httpx_client.request, self._asynchrony,
                method=method, url=(self.host + endpoint + '?' + body), headers=headers,
            )
        else:
            response = await afh(
                self._httpx_client.request, self._asynchrony,
                method=method, url=(self.host + endpoint), headers=headers, data=body,
            )
        self._log_debug(response.json())
        return response

    def _get_signature(self, timestamp: str, body: Union[str, dict]) -> str:
        param_str = timestamp + self._api_key + RECV_WINDOW + body
        hsh = hmac.new(bytes(self._secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hsh.hexdigest()
        return signature

    def _get_httpx_client(self, ) -> Union[Client, AsyncClient]:
        if self._asynchrony:
            httpx_client = httpx.AsyncClient(proxy=self.proxy)
        else:
            httpx_client = httpx.Client(proxy=self.proxy)
        return httpx_client

    def _log_debug(self, message: str) -> None:
        if self._logger is not None:
            self._logger.debug(f'{self.name} | {message}')

    @property
    def time(self, ) -> str:
        current_time = round(time.time() * 1000) - 4000
        return str(current_time)

    @property
    def proxy(self, ) -> Optional[str]:
        return f'http://{self._proxy}' if self._proxy else None

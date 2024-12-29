import base64
import json
from logging import Logger
from typing import Optional, Union, Tuple
from httpx import Client, AsyncClient, Response

import hmac
import time
import hashlib
import httpx
import pandas

from .utils import afh


class MyBybit:
    name = 'Bybit'
    host = 'https://api.bybit.com'

    def __init__(
            self,
            api_key: str,
            secret_key: str,
            passphrase: str,
            proxy: Optional[str] = None,
            logger: Optional[Logger] = None,
            asynchrony: Optional[bool] = False,
    ):
        self._api_key = api_key
        self._secret_key = secret_key
        self._passphrase = passphrase
        self._proxy = proxy
        self._logger = logger
        self._asynchrony = asynchrony
        self._httpx_client = self._get_httpx_client()

    async def check_keys(self):
        """
        url: https://api.bybit.com//v5/account/wallet-balance/accountType=UNIFIED
        """
        endpoint = '/v5/account/wallet-balance'
        method = 'GET'
        body = 'accountType=UNIFIED'
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
        except:
            pass

    def _get_httpx_client(self, ) -> Union[Client, AsyncClient]:
        if self._asynchrony:
            httpx_client = httpx.AsyncClient(proxy=self.proxy)
        else:
            httpx_client = httpx.Client(proxy=self.proxy)
        return httpx_client

    async def _httpx_request(self, method: str, endpoint: str, body: Union[str, dict]) -> Response:
        timestamp = self.time
        signature = self._get_signature(timestamp, method, endpoint, body)
        headers = {
            'OK-ACCESS-KEY': self._api_key,
            'OK-ACCESS-PASSPHRASE': self._passphrase,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-SIGN': signature,
        }
        if isinstance(body, str):
            response = await afh(
                self._httpx_client.request, self._asynchrony,
                method=method, url=(self.host + endpoint + body), headers=headers,
            )
        else:
            response = await afh(
                self._httpx_client.request, self._asynchrony,
                method=method, url=(self.host + endpoint), headers=headers, json=body,
            )
        self._log_debug(response.json())
        return response

    def _get_signature(self, timestamp: str, method: str, endpoint: str, body: Union[str, dict]) -> bytes:
        message = timestamp + method.upper() + endpoint + (json.dumps(body, separators=(',', ':')) if isinstance(body, dict) else body)
        mac = hmac.new(bytes(self._secret_key, encoding='utf-8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        signature = base64.b64encode(mac.digest())
        return signature

    def _log_debug(self, message: str) -> None:
        if self._logger is not None:
            self._logger.debug(f'{self.name} | {message}')

    @property
    def proxy(self, ) -> Optional[str]:
        return f'http://{self._proxy}' if self._proxy else None

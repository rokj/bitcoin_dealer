import sys, os, re, urllib, urllib3, httplib, time, json, hmac, hashlib, base64

from decimal import Decimal
from exchange.exchange_abstract import ExchangeAbstract

class MtGox1(ExchangeAbstract):
    """
    See:
    https://en.bitcoin.it/wiki/MtGox/API
    """

    last_price = {}

    ticker_url = { "method": "GET", "url": "https://mtgox.com/api/1/BTCUSD/public/ticker" }
    buy_url = { "method": "POST", "url": "https://mtgox.com/api/1/BTCUSD/private/order/add" }
    sell_url = { "method": "POST", "url": "https://mtgox.com/api/1/BTCUSD/private/order/add" }
    open_orders_url = { "method": "GET", "url": "https://mtgox.com/api/1/generic/private/orders" }

    key = None
    secret = None
    classname = None

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def _change_currency_url(self, url, currency):
        return re.sub(r'BTC\w{3}', r'BTC' + currency, url)

    def _create_nonce(self):
        return int(time.time() * 1000000)

    def _send_request(self, url, params, extra_headers=None):
        headers = { 'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }

        if extra_headers is not None:
            for k, v in extra_headers.iteritems():
                headers[k] = v

        http_pool = urllib3.connection_from_url(url['url'])
        response = http_pool.urlopen(url['method'], url['url'], body=urllib.urlencode(params), headers=headers)

        if response.status == 200:
            return json.loads(response.data)

        return None

    def _to_int_price(self, price, currency):
        if currency == "USD" or currency == "EUR":
            price = Decimal(price)

            return int(price * 100000)

        return None

    def _to_int_amount(self, amount):
        amount = Decimal(amount)

        return int(amount * 100000000)

    def get_orders(self):
        if not self.key or self.key is None: return
        if not self.secret or self.secret is None: return

        params = [ (u"nonce", self._create_nonce()) ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.open_orders_url, params, headers)

        if response and "result" in response and response["result"] == "success":
            return response["return"]

        return None

    def get_price(self, currency):
        if currency in self.last_price:
            return self.last_price[currency]

        self.ticker_url["url"] = self._change_currency_url(self.ticker_url["url"], currency)

        response = self._send_request(self.ticker_url, {})
        if response and "result" in response and response["result"] == "success" and "return" in response and "last_local" in response["return"]:
            self.last_price[currency] = Decimal(response["return"]["last_local"]["value"])

            return Decimal(response["return"]["last_local"]["value"])

        return None

    def get_balance(self):
        """
        For future use.
        """

        if not self.key or self.key is None: return
        if not self.secret or self.secret is None: return

        params = [ (u"nonce", self._create_nonce()) ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.balance_url, params, headers)

        if response and "result" in response and response["result"] == "success":
            return response

        return None

    def buy(self, price, amount, currency):
        """
        bid == buy
        ask == sell

        Returns order ID if order was placed successfully.
        """
        if not self.key or self.key is None: return
        if not self.secret or self.secret is None: return

        price = self._to_int_price(price, currency)
        amount = self._to_int_amount(amount)

        if not price or price is None:
            console_log("there is no conversion forumla for currency %s" % (currency))

            return None

        if not amount or amount is None: return None

        self.buy_url["url"] = self._change_currency_url(self.buy_url["url"], currency)

        params = [ ("nonce", self._create_nonce()), ("amount_int", str(amount)), ("price_int", str(price)), ("type", "bid") ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.buy_url, params, headers)

        if response and "result" in response and response["result"] == "success":
            return response["return"]

        return None

    def sell(self, price, amount, currency):
        """
        ask == sell
        """
        if not self.key or self.key is None: return
        if not self.secret or self.secret is None: return

        price = self._to_int_price(price, currency)
        amount = self._to_int_amount(amount)

        if not price or price is None:
            console_log("there is no conversion forumla for currency %s" % (currency))

            return None

        if not amount or amount is None: return None

        self.sell_url["url"] = self._change_currency_url(self.sell_url["url"], currency)

        params = [ ("nonce", self._create_nonce()), ("amount_int", str(amount)), ("price_int", str(price)), ("type", "ask") ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.sell_url, params, headers)

        if response and "result" in response and response["result"] == "success":
            return response["return"]

        return None

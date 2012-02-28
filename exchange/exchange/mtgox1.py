import sys, os, urllib, urllib3, httplib, time, json, hmac, hashlib, base64

from decimal import Decimal

class MtGox1():
    """
    See:
    https://en.bitcoin.it/wiki/MtGox/API
    """

    ticker_url = { "method": "GET", "url": "https://mtgox.com/api/1/BTCUSD/public/ticker" }
    buy_url = { "method": "POST", "url": "https://mtgox.com/api/1/BTCUSD/private/order/add" }
    sell_url = { "method": "POST", "url": "https://mtgox.com/api/1/BTCUSD/private/order/add" }
    open_orders_url = { "method": "POST", "url": "https://mtgox.com/api/1/generic/private/orders" }

    key = None
    secret = None
    currency = None
    price = None

    def __init__(self, kwargs):
        """
        We have to do this:

        self.username = username
        self.password = password
        self.key = key
        self.secret = secret
        self.currency = currency
        """

        for k, v in kwargs.iteritems():
            setattr(self, k, v)

        self._change_currency_url()

    def _change_currency_url(self):
        self.ticker_url["url"] = self.ticker_url["url"].replace('BTCUSD', 'BTC' + self.currency)

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

    def _to_int_price(self, price):
        if self.currency == "USD" or self.currency == "EUR":
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

    def get_price(self):
        """
        We get local price, and we trust mtgox on value_int being correctly
        converted to value with 0.00001 or something, so we do not have to deal with multicurrency conversion.
        """
        response = self._send_request(self.ticker_url, {})
        if response and "result" in response and response["result"] == "success" and "return" in response and "last_local" in response["return"]:
            # maybe we will need someday this
            # self.price = Decimal(ticker["return"]["last_local"]["value"])
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

    def buy(self, price, amount):
        """
        bid == buy

        Returns order ID if order was placed successfully.
        """
        if not self.key or self.key is None: return
        if not self.secret or self.secret is None: return

        price = self._to_int_price(price)
        amount = self._to_int_amount(amount)

        if not price or price is None:
            console_log("there is no conversion forumla for currency %s" % (self.currency))

            return None

        if not amount or amount is None: return None

        params = [ ("nonce", self._create_nonce()), ("amount_int", str(amount)), ("price_int", str(price)), ("type", "bid") ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.buy_url, params, headers)

        if response and "result" in response and response["result"] == "success":
            return response["return"]

        return None

    def sell(self, price, amount):
        """
        ask == sell
        """
        if not self.key or self.key is None: return
        if not self.secret or self.secret is None: return

        price = self._to_int_price(price)
        amount = self._to_int_amount(amount)

        if not price or price is None:
            console_log("there is no conversion forumla for currency %s" % (self.currency))

            return None

        if not amount or amount is None: return None

        params = [ ("nonce", self._create_nonce()), ("amount_int", str(amount)), ("price_int", str(price)), ("type", "ask") ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.sell_url, params, headers)

        if response and "result" in response and response["result"] == "success":
            return response["return"]

        return None

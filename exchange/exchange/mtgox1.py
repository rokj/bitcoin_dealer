import sys, os, re, urllib, urllib3, httplib, time, json, hmac, hashlib, base64

from decimal import Decimal
from common.functions import console_log
from exchange.exchange_abstract import ExchangeAbstract, Order

class MtGox1(ExchangeAbstract):
    """
    See:
    https://en.bitcoin.it/wiki/MtGox/API
    """

    _last_price = {}
    _order = None

    ticker_url = { "method": "GET", "url": "http://data.mtgox.com/api/1/BTCUSD/ticker_fast" }
    buy_url = { "method": "POST", "url": "https://data.mtgox.com/api/1/BTCUSD/private/order/add" }
    sell_url = { "method": "POST", "url": "https://data.mtgox.com/api/1/BTCUSD/private/order/add" }
    order_url = { "method": "POST", "url": "https://data.mtgox.com/api/1/generic/private/order/result" }
    open_orders_url = { "method": "POST", "url": "https://data.mtgox.com/api/1/generic/private/orders" }
    cancel_url = { "method": "POST", "url": " https://data.mtgox.com/api/1/BTCUSD/private/order/cancel" }
    
    key = None
    secret = None
    classname = None

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, order):
        self._order = order

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

        self._last_price = {}
        self._order = None

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
        ret_price = None

        if currency == "USD" or currency == "EUR" or currency == "GBP" or currency == "PLN" or currency == "CAD" or currency == "AUD" or currency == "CHF" or currency == "CNY" or currency == "NZD" or currency == "RUB" or currency == "DKK" or currency == "HKD" or currency == "SGD" or currency == "THB":
            ret_price = Decimal(price)
            ret_price = int(price * 100000)
        elif currency == "JPY" or currency == "SEK":
            ret_price = Decimal(price)
            ret_price = int(price * 1000)

        return ret_price

    def _to_int_amount(self, amount):
        amount = Decimal(amount)

        return int(amount * 100000000)

    def get_order(self, trade):
        """
        Method gets particular order.
        """

        if not self.key or self.key is None:
            console_log("mtgox: key not set; check settings.py")
            return

        if not self.secret or self.secret is None:
            console_log("mtgox: secret not set; check settings.py")
            return

        order_type = ""
        if trade.buy_or_sell == True:
            order_type = "bid"
        elif trade.buy_or_sell == False:
            order_type = "ask"
        params = [ ("nonce", self._create_nonce()), ("order", trade.exchange_oid), ("type", order_type) ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.order_url, params, headers)
        if response and u"result" in response and response[u"result"] == u"success":
            order = Order()
            if u"trades" in response[u"return"]:
                order.trades = response[u"return"][u"trades"]

                sum_price = 0
                sum_amount = 0
                for exchange_trade in response[u"return"]["trades"]:
                    if str(trade.currency) == str(exchange_trade[u"currency"]):
                        sum_price += Decimal(exchange_trade[u"amount"][u"value"]) * Decimal((exchange_trade[u"price"][u"value"]))
                        sum_amount += Decimal(exchange_trade[u"amount"][u"value"])

                order.sum_price = sum_price
                order.sum_amount = sum_amount

                return order
        elif response and u"result" in response and response[u"result"] == u"error":
            return {"error": response[u"error"]}

        return None

    def get_orders(self):
        """
        Method gets open orders.
        """

        if not self.key or self.key is None:
            console_log("mtgox: key not set; check settings.py")
            return

        if not self.secret or self.secret is None:
            console_log("mtgox: secret not set; check settings.py")
            return

        params = [ (u"nonce", self._create_nonce()) ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.open_orders_url, params, headers)

        if response and u"result" in response and response[u"result"] == u"success":
            return response[u"return"]

        return None

    def get_last_price(self, currency):
        if currency in self._last_price:
            return self._last_price[currency]

        self.ticker_url["url"] = self._change_currency_url(self.ticker_url["url"], currency)

        response = self._send_request(self.ticker_url, {})
        if response and u"result" in response and response[u"result"] == u"success" and u"return" in response and u"last_local" in response[u"return"]:
            self._last_price[currency] = Decimal(response[u"return"][u"last_local"][u"value"])

            return Decimal(response[u"return"][u"last_local"][u"value"])

        return None

    def get_balance(self):
        """
        For future use.
        """

        if not self.key or self.key is None:
            console_log("mtgox: key not set; check settings.py")
            return

        if not self.secret or self.secret is None:
            console_log("mtgox: secret not set; check settings.py")
            return


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
        if not self.key or self.key is None:
            console_log("mtgox: key not set; check settings.py")
            return None

        if not self.secret or self.secret is None:
            console_log("mtgox: secret not set; check settings.py")
            return None


        price = self._to_int_price(price, currency)
        amount = self._to_int_amount(amount)

        if not price or price is None:
            console_log("mtgox: there is no conversion forumla for currency %s" % (currency))

            return None

        if not amount or amount is None: return None


        self.buy_url["url"] = self._change_currency_url(self.buy_url["url"], currency)

        params = [ ("nonce", self._create_nonce()), ("amount_int", str(amount)), ("price_int", str(price)), ("type", "bid") ]
        headers = { 'Rest-Key': self.key, 'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), urllib.urlencode(params), hashlib.sha512).digest())) }

        response = self._send_request(self.buy_url, params, headers)

        if response and u"result" in response and response[u"result"] == u"success":
            return response[u"return"]

        return None

    def sell(self, price, amount, currency):
        """
        ask == sell
        """

        if not self.key or self.key is None:
            console_log("mtgox: key not set; check settings.py")
            return

        if not self.secret or self.secret is None:
            console_log("mtgox: secret not set; check settings.py")
            return


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

        if response and u"result" in response and response[u"result"] == u"success":
            return response[u"return"]

        return None

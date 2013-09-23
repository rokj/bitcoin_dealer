import sys, os, re, urllib, urllib3, httplib, time, json, hmac, hashlib, base64

from decimal import Decimal
from exchange.exchange_abstract import ExchangeAbstract, Order

class BitStamp1(ExchangeAbstract):
    """
    See:
    https://www.bitstamp.net/api/
    """

    _last_price = {}
    _order = None

    ticker_url = { "method": "GET", "url": "https://www.bitstamp.net/api/ticker/" }
    buy_url = { "method": "POST", "url": "https://www.bitstamp.net/api/buy/" }
    sell_url = { "method": "POST", "url": "https://www.bitstamp.net/api/sell/" }
    #order_url = { "method": "POST", "url": "https://data.mtgox.com/api/1/generic/private/order/result" }
    #open_orders_url = { "method": "POST", "url": "https://data.mtgox.com/api/1/generic/private/orders" }

    user = None
    password = None
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
        response = http_pool.urlopen(url['method'], url['url'], body=urllib.urlencode(params))#, headers = headers)

        if response.status == 200:
            return json.loads(response.data)

        return None

    def _to_int_price(self, price, currency):
        ret_price = None
        
        ret_price = Decimal(price).quantize(Decimal('0.01'))
            #ret_price = int(price * 100000)

        return ret_price

    def _to_int_amount(self, amount):
        amount = Decimal(amount).quantize(Decimal('0.01'))
        return amount

    def get_last_price(self, currency):
        if currency in self._last_price:
            return self._last_price[currency]

        self.ticker_url["url"] = self._change_currency_url(self.ticker_url["url"], currency)

        response = self._send_request(self.ticker_url, {})
        if response:
            self._last_price[currency] = Decimal(response[u"last"])
            return Decimal(response[u"last"])

        return None
    
    def get_orders(self):
        return None

    def buy(self, price, amount, currency):
        """
        bid == buy
        ask == sell

        Returns order ID if order was placed successfully.
        """
        if not self.user or self.user is None: return None
        if not self.password or self.password is None: return None

        price = self._to_int_price(price, currency)
        amount = self._to_int_amount(amount)

        if not price or price is None:
            #console_log("there is no conversion forumla for currency %s" % (currency))

            return None

        if not amount or amount is None: return None


        self.buy_url["url"] = self._change_currency_url(self.buy_url["url"], currency)
        params = {'user': self.user, 'password': self.password, "amount": str(amount), "price": str(price)}
        # headers = {  }
        response = self._send_request(self.buy_url, params)
        print response
        if response and u"id" in response:
            return response[u"id"]

        return None

    def sell(self, price, amount, currency):
        """
        ask == sell
        """
        
        if not self.user or self.user is None: return None
        if not self.password or self.password is None: return None
        price = self._to_int_price(price, currency)
        amount = self._to_int_amount(amount)
        
        if not price or price is None:
            #console_log("there is no conversion forumla for currency %s" % (currency))

            return None

        if not amount or amount is None: return None
        self.sell_url["url"] = self._change_currency_url(self.sell_url["url"], currency)
        
        
        params = {'user': self.user, 'password': self.password, "amount": str(amount), "price": str(price)}
       
        response = self._send_request(self.sell_url, params)
        
        if response and u"id" in response:
            return response[u"id"]

        return None
    
    def get_order(self, trade):
        return None
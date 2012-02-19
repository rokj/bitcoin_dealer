import sys, os, urllib, urllib2, time, json, hmac, hashlib, base64

class MtGox2():
    """
    See:
    https://mtgox.com/support/tradeAPI
    https://en.bitcoin.it/wiki/MtGox/API#Authentication

    examples:
    https://mtgox.com/code/buyBTC.php?name=%s&pass=%s&amount=%s&price=%s
    https://mtgox.com/code/getOrders.php?name=%s&pass=%s
    """    

    ticker_url = "https://mtgox.com/api/1/BTCUSD/public/ticker"

    buy_url = "https://mtgox.com/api/0/buyBTC.php"
    sell_url = "https://mtgox.com/api/0/sellBTC.php"
    orders_url = "https://mtgox.com/code/getOrders.php"
    balance_url = "https://mtgox.com/api/0/getFunds.php"

    username = None
    password = None
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

        self._change_currency_urls()

    def _change_currency_urls(self):
        self.ticker_url = self.ticker_url.replace('BTCUSD', 'BTC' + self.currency)

    def _create_nonce(self):
        return int(time.time()*100)

    def _send_request(self, url, params, extra_headers = None):
        headers = { 'X_REQUESTED_WITH' :'XMLHttpRequest', 'ACCEPT': 'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/5.0 (compatible; bitcoin dealer client; v0.3.0; using Python)' }
        if extra_headers is not None:
            for k, v in extra_headers.iteritems():
                headers[k] = v

        data = urllib.urlencode(params)
        req = urllib2.Request(url, data, headers)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()

        return json.loads(response) 

    def get_orders(self):
        params = { 'name': self.username, 'pass': self.password }
        return self._send_request(self.orders_url, params)

    def get_price(self):
        """
        We get local price...
        """

        ticker = self._send_request(self.ticker_url, {})
        if ticker and "result" in ticker and ticker["result"] == "success" and "return" in ticker and "last_local" in ticker["return"]:
            # maybe we will need someday this
            # self.price = ticker["return"]
            return ticker["return"]["last_local"]["value"]

        return None

    def get_balance(self):
        if not self.username or self.username is None: return
        if not self.password or self.password is None: return
        if not self.key or self.key is None: return
        if not self.secret or self.secret is None: return

        params = { 'name': self.username, 'pass': self.password, 'nonce': self._create_nonce() }
        headers = { 'Rest-Key': self.key, 'Rest-Sign': hmac.new(base64.b64decode(self.secret), '&'.join(params), hashlib.sha512) }

        response = self._send_request(self.balance_url, params, headers)
        if response:
            return response

        return None

    def buy(self, price, amount):
        if not price or price is None: return
        if not amount or amount is None: return
        if not self.username or self.username is None: return
        if not self.password or self.password is None: return

        params = { 'name': self.username, 'pass': self.password, 'nonce': self._create_nonce(), 'amount': amount, 'price': price, 'Currency': self.currency }
        headers = { 'Rest-Key': self.key, 'Rest-Sign': hmac.new(base64.b64decode(self.secret), '&'.join(params), hashlib.sha512) }
        response = self._send_request(self.buy_url, params, headers)

        if response:
            return response

        return None
    
    def sell(self, price, amount):
        if not price or price is None: return
        if not amount or amount is None: return
        if not self.username or self.username is None: return
        if not self.password or self.password is None: return

        params = { 'name': self.username, 'pass': self.password, 'nonce': self._create_nonce(), 'amount': amount, 'price': price, 'Currency': self.currency }
        headers = { 'Rest-Key': self.key, 'Rest-Sign': hmac.new(base64.b64decode(self.secret), '&'.join(params), hashlib.sha512) }
        response = self._send_request(self.sell_url, params, headers)

        if response:
            return response

        return None

        

from abc import ABCMeta, abstractmethod, abstractproperty
import bitcoin_dealer.settings as settings

class OrderAbstract:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._trades = None

    def get_trades(self):
        return self._trades
    def set_trades(self, value):
        self._trades = value
    def del_trades(self):
        del self._trades
    trades = abstractproperty(get_trades, set_trades, del_trades)

class ExchangeAbstract:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._last_price = {}
        # self._order = OrderAbstract()

    def get_last_price(self, currency):
        return self._last_price[currency]
    def set_last_price(self, currency):
        self._last_price[currency] = {}
    def del_last_price(self):
        self._last_price = {}
        del self._last_price
    last_price = abstractproperty(get_last_price, set_last_price, del_last_price)

    """
    def get_order(self):
        return self._order
    def set_order(self, value):
        self._order = value
    def del_order(self):
        del self._order
    order = abstractproperty(getorder, setorder, delorder)

    def __init__(self):
        self._order = None
    """
            
    @abstractmethod
    def get_orders(self):
        """
        Retrieves orders for particular exchange.

        This method is used for check_status function in scripts/dealing.py,
        but right now, when only MtGox API version 1 is implemented, returned
        data is not structured. I/you should do it, when implementing support
        for other exchanges.
        """

        return None

    @abstractmethod
    def get_price(self, currency):
        """
        Retrieves last price for particular exchange.

        Should return Decimal value of a price.
        """

        return None

    @abstractmethod
    def buy(self, price, amount, currency):
        """ 
        bid == buy

        Should return order ID if order was placed successfully.
        """

        return None

    @abstractmethod
    def sell(self, price, amount, currency):
        """ 
        bid == buy

        Should return order ID if order was placed successfully.
        """

        return None

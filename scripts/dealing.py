import sys, os, time, datetime
import urllib2
from django.core.management import setup_environ
from django import db
from decimal import *

sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../bitcoin_dealer'))

from bitcoin_dealer.exchange.exchange.mtgox1 import MtGox1
from bitcoin_dealer.exchange.models import Trade, TradeLog, Exchange
from bitcoin_dealer.exchange.exchange_abstract import ExchangeAbstract
import bitcoin_dealer.settings as settings

def console_log(message):
    now = datetime.datetime.now()
    print "%s - %s" % (now.strftime("%Y-%m-%d %H:%M:%S"), message)

def trade(trades):
    for trade in trades:
        if trade.exchange.name in exchanges:
            last_price = exchanges[trade.exchange.name].get_price(trade.currency.name)
        else:
            continue
        
        if last_price is None: continue

        last_price = Decimal(last_price)

        try:
            watch_price = Decimal(trade.watch_price)
            # we are BUYING, when last price is higher or equal to watch price (lp_higher == True) and there is no related "sell" order
            if trade.active == True and trade.lp_higher == True and trade.buy_or_sell == True and trade.related is None:
                if last_price >= watch_price:
                    response = exchanges[trade.exchange.name].buy(trade.price, trade.amount. trade.currency.name)

                    if response and response is not None:
                        trade.active = False
                        trade.status = "buying"
                        trade.exchange_oid = response
                        trade.save()

                        trade_log = TradeLog(created_by=trade.user, trade=trade, log="buying", log_desc="Buying %s." % (trade.pk))
                        trade_log.save()

                        if settings.bd_debug == True:
                            console_log("buying, when last price (%s) is higher or equal than watch price (%s) and there is no related sell order (buying at price: %s, amount: %s)" % (last_price, trade.watch_price, trade.price, trade.amount))

            # we are BUYING, when last price is lower or equal to watch price (lp_higher == False) and there is no related "sell" order
            elif trade.active == True and trade.lp_higher == False and trade.buy_or_sell == True and trade.related is None:
                if last_price <= watch_price:
                    response = exchanges[trade.exchange.name].buy(trade.price, trade.amount, trade.currency.name)

                    if response and response is not None:
                        trade.active = False
                        trade.status = "buying"
                        trade.exchange_oid = response
                        trade.save()

                        trade_log = TradeLog(created_by=trade.user, trade=trade, log="buying", log_desc="Buying %s." % (trade.pk))
                        trade_log.save()

                        if settings.bd_debug == True:
                            console_log("buying, when last price (%s) is lower or equal that watch price (%s) and there is no related sell order (buying at price: %s, amount: %s)" % (last_price, trade.watch_price, trade.price, trade.amount))

            # we are BUYING, when last price is higher or equal to watch price (lp_higher == True) and related "sell" order has been fully "sold"
            elif trade.active == True and trade.lp_higher == True and trade.buy_or_sell == True and trade.related is not None:
                if trade.related.status == "sold" and trade.status == "waiting":
                    if last_price >= watch_price:
                        response = exchanges[trade.exchange.name].buy(pritrade.price, trade.amount, trade.currency.name)

                        if response and response is not None:
                            trade.active = False
                            trade.status = "buying"
                            trade.exchange_oid = response
                            trade.save()

                            trade_log = TradeLog(created_by=trade.user, trade=trade, log="buying", log_desc="Buying %s (related %s sold)." % (trade.pk, trade.related.pk))
                            trade_log.save()

                            if settings.bd_debug == True:
                                console_log("buying, when last price (%s) is higher or equal to watch price (%s) and related sell order was sold (buying at price: %s, amount: %s, related: %s)" % (last_price, trade.watch_price, trade.price, trade.amount, trade.related.pk))

            # we are BUYING, when last price is lower or equal to watch price (lp_hihger == False) and related "sell" order has been fully "sold"
            elif trade.active == True and trade.lp_higher == False and trade.buy_or_sell == True and trade.related is not None:
                if trade.related.status == "sold" and trade.status == "waiting":
                    if last_price <= watch_price:
                        response = exchanges[trade.exchange.name].buy(trade.price, trade.amount, trade.currency.name)

                        if response and response is not None:
                            trade.active = False
                            trade.status = "buying"
                            trade.exchange_oid = response
                            trade.save()

                            trade_log = TradeLog(created_by=trade.user, trade=trade, log="buying", log_desc="Buying %s (related %s sold)." % (trade.pk, trade.related.pk))
                            trade_log.save()

                            if settings.bd_debug == True:
                                console_log("buying, when last price (%s) is lower or equal to watch price (%s) and related sell order was sold (buying at price: %s, amount: %s, related: %s)" % (last_price, trade.watch_price, trade.price, trade.amount, trade.related.pk))

            # we are SELLING, when last price is higher or equal to watch price (lp_higher == True) and there is no related "buy" order
            elif trade.active == True and trade.lp_higher == True and trade.buy_or_sell == False and trade.related is None:
                if last_price >= watch_price:
                    response = exchanges[trade.exchange.name].sell(trade.price, trade.amount, trade.currency.name)

                    if response and response is not None:
                        trade.active = False
                        trade.status = "selling"
                        trade.exchange_oid = response
                        trade.save()

                        trade_log = TradeLog(created_by=trade.user, trade=trade, log="selling", log_desc="Selling %s." % (trade.pk))
                        trade_log.save()

                        if settings.bd_debug == True:
                            console_log("selling, when last price (%s) is higher or equal to watch price (%s) and there is no related buy order (selling at price: %s, amount: %s)" % (last_price, trade.watch_price, trade.price, trade.amount))

            # we are SELLING, when last price is lower or equal to watch price (lp_higher == False) and there is no related "buy" order
            elif trade.active == True and trade.lp_higher == False and trade.buy_or_sell == False and trade.related is None:
                if last_price <= watch_price:
                    response = exchanges[trade.exchange.name].sell(trade.price, trade.amount, trade.currency.name)

                    if response and response is not None:
                        trade.active = False
                        trade.status = "selling"
                        trade.exchange_oid = response
                        trade.save()

                        trade_log = TradeLog(created_by=trade.user, trade=trade, log="selling", log_desc="Selling %s." % (trade.pk))
                        trade_log.save()

                        if settings.bd_debug == True:
                            console_log("selling, when last price (%s) is lower or equal to watch price (%s) and there is no related buy order (selling at price: %s, amount: %s)" % (last_price, trade.watch_price, trade.price, trade.amount))

            # we are SELLING, when last price is higher or equal to watch price (lp_higher == True) and related "buy" order has been fully "bought"
            elif trade.active == True and trade.lp_higher == True and trade.buy_or_sell == False and trade.related is not None:
                if trade.related.status == "bought" and trade.status == "waiting":
                    if last_price >= watch_price:
                        response = exchanges[trade.exchange.name].sell(trade.price, trade.amount, trade.currency.name)

                        if response and response is not None:
                            trade.active = False
                            trade.status = "selling"
                            trade.exchange_oid = response
                            trade.save()

                            trade_log = TradeLog(created_by=trade.user, trade=trade, log="selling", log_desc="Selling %s (related %s bought)." % (trade.pk, trade.related.pk))
                            trade_log.save()

                            if settings.bd_debug == True:
                                console_log("selling, when last price (%s) is higher or equal to watch price (%s) and related buy was bought (selling at price: %s, amount: %s, related: %s)" % (last_price, trade.watch_price, trade.price, trade.amount, trade.related.pk))

            # we are SELLING, when last price is lower or equal to watch price and related "buy" order has been fully "bought"
            elif trade.active == True and trade.lp_higher == False and trade.buy_or_sell == False and trade.related is not None:
                if trade.related.status == "bought" and trade.status == "waiting":
                    if last_price <= watch_price:
                        response = exchanges[trade.exchange.name].sell(trade.price, trade.amount, trade.currency.name)

                        if response and response is not None:
                            trade.active = False
                            trade.status = "selling"
                            trade.exchange_oid = response
                            trade.save()

                            trade_log = TradeLog(created_by=trade.user, trade=trade, log="selling", log_desc="Selling %s (related %s bought)." % (trade.pk, trade.related.pk))
                            trade_log.save()

                            if settings.bd_debug == True:
                                console_log("selling, when last price (%s) is lower or equal to watch price (%s) and related buy was bought (selling at price: %s, amount: %s, related: %s)" % (last_price, trade.watch_price, trade.price, trade.amount, trade.related.pk))
        except:
            raise
"""
id: Order ID
type: 1 for sell order or 2 for buy order
status: 1 for active, 2 for not enough funds
"""
def check_status(trades, orders):
    for trade in trades:
        found = None
        for order in orders:
            if str(trade.exchange_oid) == str(order[u"oid"]):
                found = order
                break
        if found is not None:
            """
            This will be used in future. Maybe. :)

            if trade.status == "selling" and found["type"] == "1" and found["status"] == "2":
                trade.status = "not enough funds"
                trade.save()

                trade_log = TradeLog(created_by=trade.user, trade=trade, log="not enough funds", log_desc="Not enough funds for trade %s." % (trade.pk))
                trade_log.save()
                if (settings.bd_debug == True):
					console_log("not enoguh funds for selling...")
            if trade.status == "buying" and found["type"] == "2" and found["status"] == "2":
                trade.status = "not enough funds"
                trade.save()

                trade_log = TradeLog(created_by=trade.user, trade=trade, log="not enough funds", log_desc="Not enough funds for trade %s." % (trade.pk))
                trade_log.save()
                if (settings.bd_debug == True):
					console_log("not enoguh funds for buying...")
            """
            pass
        else:
            if trade.status == "selling":
                trade.status = "sold"
                trade.save()

                trade_log = TradeLog(created_by=trade.user, trade=trade, log="sold", log_desc="Sold trade %s." % (trade.pk))
                trade_log.save()
                if (settings.bd_debug == True):
				    console_log("sold %s bitcoins for %s %s" % (trade.amount, trade.price, settings.mtgox_currency))
            elif trade.status == "buying":
                trade.status = "bought"
                trade.save()

                trade_log = TradeLog(created_by=trade.user, trade=trade, log="bought", log_desc="Bought trade %s." % (trade.pk))
                trade_log.save()
                if (settings.bd_debug == True):
					console_log("bought %s bitcoins for %s %s" % (trade.amount, trade.price, settings.mtgox_currency))

while True:
    time.sleep(settings.check_interval)
    try:
        exchanges = {}
        active_exchanges = Exchange.objects.filter(active=True)
        for exchange in active_exchanges:
            if exchange.name in settings.EXCHANGES:
                exchanges[exchange.name] = getattr(sys.modules[__name__], settings.EXCHANGES[exchange.name]['classname'])(settings.EXCHANGES[exchange.name]) # with (settings.EXCHANGES[exchange.name]) at the end, constructor of class gets called with settings paramaters http://stackoverflow.com/questions/553784/can-you-use-a-string-to-instantiate-a-class-in-python

        my_trades = Trade.objects.filter(exchange__in=active_exchanges, active=True)
        trade(my_trades)

        # we check for statuses of our orders
        all_my_trades = Trade.objects.all()
        
        my_open_orders = []
        for exchange, exchange_data in exchanges.iteritems():
            open_orders = exchanges[exchange].get_orders()
            if open_orders is not None:
                # when we will implement another exchange, we will need following line instead of the second following line
                # my_open_orders.append(open_orders)
                my_open_orders = open_orders

        if all_my_trades is not None and len(all_my_trades) > 0 and my_open_orders is not None:
            check_status(all_my_trades, my_open_orders)
            if (settings.bd_debug == True):
	            console_log("just checked statuses of orders...")

        if (settings.bd_debug == True):
            console_log("sleeping %d seconds..." % settings.check_interval)

    except urllib2.URLError as err:
        console_log("could not connect to some url: %s" % (err))
        pass
    except ValueError as (err):
        # got this error once
        console_log("No JSON object could be decoded ???: %s " % (err))
        pass
    except:
        raise

    db.reset_queries()

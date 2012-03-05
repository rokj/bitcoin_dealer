from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from common.models import Skeleton, SkeletonU

SELL_TIME = ( 
    ('now', 'now'),
    ('at sell price', 'at sell price'),
    ('after fixed time', 'after fixed time')
)

TRADE_STATUS = (
    ('waiting', 'waiting'),
    ('buying', 'buying'),
    ('bought', 'bought'),
    ('selling', 'selling'),
    ('sold', 'sold'),
    ('stop', 'stop'),
    ('stopped', 'stopped'),
    ('cancel', 'cancel'),
    ('canceled', 'canceled'),
    ('not enough funds', 'not enough funds')
)

LOG = (
    ('waiting', 'waiting'),
    ('buying', 'buying'),
    ('bought', 'bought'),
    ('selling', 'selling'),
    ('sold', 'sold'),
    ('stop', 'stop'),
    ('stopped', 'stopped'),
    ('cancel', 'cancel'),
    ('canceled', 'canceled'),
    ('not enough funds', 'not enough funds'),
    ('could not get price', 'could not get price'),
    ('could not get orders', 'could not get orders'),
    ('custom', 'custom')
)

class Currency(SkeletonU):
    name = models.CharField(_('Currency name'), max_length=30, null=False, blank=False, unique=True)
    abbreviation = models.CharField(_('Abbreviation'), max_length=5, null=False, blank=False, unique=True)
    symbol = models.CharField(_('Currency symbol'), max_length=3, null=True, blank=True)

    def __unicode__(self):
        return u'%s' % (self.abbreviation)

class Exchange(SkeletonU):
    name = models.CharField(_('Exchange name'), max_length=40, null=False, blank=False, unique=True, db_index=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    url = models.URLField(_('URL of change'), max_length=255, blank=True, null=True, verify_exists=False)
    currencies = models.ManyToManyField(Currency, null=True, blank=True) # for future use
    active = models.BooleanField(_('Active or not'), help_text=_('If active is set to false on exchange, then all trades for this exchange will be deactivated and cancelled (if exchange does support this action).'), default=False, null=False, blank=False)

    def __unicode__(self):
        return u"%s" % (self.name)

"""
For future
class UserExchangeCurrency(SkeletonU):
    user = models.ForeignKey(User, related_name='(app_label)s_%(class)s_user', null=False, blank=False)
    exchange = models.ForeignKey(Exchange, related_name='(app_label)s_%(class)s_user', null=False, blank=False)
    currency = models.ForeignKey(Currency, related_name='(app_label)s_%(class)s_user', null=False, blank=False)
    active = models.BooleanField(_('Active or not'), help_text=_('If active is set to false on exchange, then all trades for this exchange will be deactivated and cancelled (if exchange does support this action).'), default=False, null=False, blank=False)
"""

class Trade(SkeletonU):
    """
    buy_or_sell == True => BUY
    buy_or_sell == False => SELL
    """

    user = models.ForeignKey(User, related_name='(app_label)s_%(class)s_user', null=False, blank=False)
    lp_higher = models.BooleanField(_('Is last price price higher/lower?'), help_text=_('TRUE == if last price is higher or equal to watch price; FALSE == if last price is lower or equal to watch price'), default=False, null=False, blank=False)
    buy_or_sell = models.BooleanField(_('Buy or sell?'), help_text=_('TRUE == buy; FALSE == sell'), default=False, null=False, blank=False)
    watch_price = models.DecimalField(_('Price to watch'), max_digits=10, decimal_places=5, null=False, blank=False)
    price = models.DecimalField(_('Buy or sell at price'), max_digits=10, decimal_places=5, null=False, blank=False)
    amount = models.DecimalField(_('Amount'), max_digits=16, decimal_places=8, null=False, blank=False)
    status = models.CharField(_('Status of trade'), help_text=_('status of trade'), max_length=30, null=False, blank=False, choices=TRADE_STATUS, default='waiting')
    active = models.BooleanField(_('Active or not'), help_text=_('active == TRUE, not active == FALSE'), default=False, null=False, blank=False)
    exchange_oid = models.CharField(_('Exchanges order ID'), help_text=_('Some exchanges returned id of a trade or something (we have it in format of http://en.wikipedia.org/wiki/UUID)'), max_length=36, null=True, blank=True, db_index=True) 
    related = models.ForeignKey('self', help_text=_('Only if related order was successfully executed, only then this order will be executed also'), null=True, blank=True)
    exchange = models.ForeignKey(Exchange, related_name='(app_label)s_%(class)s_exchange', null=False, blank=False) 
    currency = models.ForeignKey(Currency, related_name='(app_label)s_%(class)s_currency', null=False, blank=False)

    def total(self):
        return u'%s' % (str(round(Decimal(self.price*self.amount), 8)))

    def __unicode__(self):
        return u'%s - %s %s %s' % (self.pk, self.watch_price, self.price, self.amount)

class TradeLog(SkeletonU):
    datetime = models.DateTimeField(_('Datetime of log'), auto_now=True, auto_now_add=True, null=False, blank=False)
    trade = models.ForeignKey(Trade, related_name='%(app_label)s_%(class)s_trade', null=False, blank=False)
    log = models.CharField(_('Log'), max_length=40, null=False, blank=False, choices=LOG)
    log_desc = models.TextField(_('Log description'), null=False, blank=False)

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

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

class Trade(models.Model):
    """
    buy_or_sell == True => BUY
    buy_or_sell == False => SELL
    """

    user = models.ForeignKey(User, related_name='(app_label)s_%(class)s_user', null=False, blank=False)
    lp_higher = models.BooleanField(_('Is last price price higher/lower?'), help_text=_('TRUE == if last price is higher or equal to watch price; FALSE == if last price is lower or equal to watch price'), default=False, null=False, blank=False)
    buy_or_sell = models.BooleanField(_('Buy or sell?'), help_text=_('TRUE == buy; FALSE == sell'), default=False, null=False, blank=False)
    watch_price = models.DecimalField(_('Price to watch'), max_digits=10, decimal_places=5, null=False, blank=False)
    price = models.DecimalField(_('Buy or sell at price'), max_digits=10, decimal_places=5, null=False, blank=False)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=5, null=False, blank=False)
    exchange_order_id = models.PositiveIntegerField(_('Exchange order id'), null=True, blank=True)
    status = models.CharField(_('Status of trade'), help_text=_('status of trade'), max_length=30, null=False, blank=False, choices=TRADE_STATUS, default='waiting')
    active = models.BooleanField(_('Active or not'), help_text=_('active == TRUE, not active == FALSE'), default=False, null=False, blank=False)
    related = models.ForeignKey('self', help_text=_('Only if related order was successfully executed, only then this order will be executed also'), null=True, blank=True)

    datetime_created = models.DateTimeField(auto_now=False, auto_now_add=True, null=False, blank=False)
    datetime_updated = models.DateTimeField(auto_now=True, auto_now_add=True, null=False, blank=False)
    datetime_deleted = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_created_by', null=False, blank=False)
    updated_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_updated_by', null=True, blank=True)

    def __unicode__(self):
        return u'%s - %s %s %s' % (self.pk, self.watch_price, self.price, self.amount)

class TradeLog(models.Model):
    datetime = models.DateTimeField(_('Datetime of log'), auto_now=True, auto_now_add=True, null=False, blank=False)
    trade = models.ForeignKey(Trade, related_name='%(app_label)s_%(class)s_trade', null=False, blank=False)
    log = models.CharField(_('Log'), max_length=40, null=False, blank=False, choices=LOG)
    log_desc = models.TextField(_('Log description'), null=False, blank=False)
    

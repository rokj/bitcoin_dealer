from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.forms.widgets import Select
from models import Trade, TradeLog, Currency, Exchange

class ExchangeAdmin(admin.ModelAdmin):
    exclude = ('user', 'created_by', 'updated_by', 'datetime_deleted', )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user

        obj.save()

    # Kudos to http://www.b-list.org/weblog/2008/dec/24/admin/
    def has_change_permission(self, request, obj=None):
        has_class_permission = super(ExchangeAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.created_by.id:
            return False
        return True

    # Kudos to http://www.b-list.org/weblog/2008/dec/24/admin/
    def queryset(self, request):
        if request.user.is_superuser:
            return Trade.objects.all()
        return Exchange.objects.filter(created_by = request.user)

class CurrencyAdmin(admin.ModelAdmin):
    exclude = ('user', 'created_by', 'updated_by', 'datetime_deleted', )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user

        obj.save()

    # Kudos to http://www.b-list.org/weblog/2008/dec/24/admin/
    def has_change_permission(self, request, obj=None):
        has_class_permission = super(CurrencyAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.created_by.id:
            return False
        return True

    # Kudos to http://www.b-list.org/weblog/2008/dec/24/admin/
    def queryset(self, request):
        if request.user.is_superuser:
            return Trade.objects.all()
        return Currency.objects.filter(created_by = request.user)

class TradeAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TradeAdminForm, self).__init__(*args, **kwargs)
        self.fields["related"].widget = Select()
        self.fields["related"].queryset = Trade.objects.order_by('-id',)

class TradeAdmin(admin.ModelAdmin):
    exclude = ('user', 'created_by', 'updated_by', 'datetime_deleted', )
    list_display = ('pk', '_buy_or_sell', '_watch_price', 'price', 'amount', 'currency', 'exchange', 'status', 'related', 'active', 'datetime_updated', )
    fields = ('watch_price', 'lp_higher', 'buy_or_sell', 'price', 'currency', 'amount', 'related', 'exchange', 'exchange_oid', 'status', 'active',)
    ordering = ('-id',)
    readonly_fields = ( 'exchange_oid', )
    form = TradeAdminForm

    def _watch_price(self, obj):
        if obj.lp_higher == True:
            return _('if price is') + ' >= %s' % (obj.watch_price)
        else:
            return _('if price is') + ' <= %s' % (obj.watch_price)
    _watch_price.short_description = 'Price to watch'
    _watch_price.admin_order_field = 'watch_price'

    def _buy_or_sell(self, obj):
        if obj.buy_or_sell == True:
            return _('Buying')
        
        else:
            return _('Selling')
    _buy_or_sell.short_description = 'Buying or selling'
    _buy_or_sell.admin_order_field = 'buy_or_sell'

    # Kudos to http://www.b-list.org/weblog/2008/dec/24/admin/
    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
            obj.created_by = request.user
        else:
            obj.updated_by = request.user

        obj.save()

    # Kudos to http://www.b-list.org/weblog/2008/dec/24/admin/
    def has_change_permission(self, request, obj=None):
        has_class_permission = super(TradeAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.created_by.id:
            return False
        return True

    # Kudos to http://www.b-list.org/weblog/2008/dec/24/admin/
    def queryset(self, request):
        if request.user.is_superuser:
            return Trade.objects.all()
        return Trade.objects.filter(created_by = request.user)

class TradeLogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'datetime', 'trade', 'log', 'log_desc',)

admin.site.register(Trade, TradeAdmin)
admin.site.register(TradeLog, TradeLogAdmin)
admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(Currency, CurrencyAdmin)

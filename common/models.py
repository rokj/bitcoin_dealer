from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Skeleton(models.Model):
    datetime_created = models.DateTimeField(auto_now=False, auto_now_add=True, null=False, blank=False)
    datetime_updated = models.DateTimeField(auto_now=True, auto_now_add=True, null=False, blank=False)
    datetime_deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

class SkeletonU(Skeleton):
    '''
    Skeleton model with Users included.
    '''
    created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_created_by', null=False)
    updated_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_updated_by', null=True, blank=True)

    class Meta:
        abstract = True

class Settings(SkeletonU):
    key = models.CharField(_('Key'), max_length=50, null=False, blank=False, unique=True)
    value = models.CharField(_('Value'), max_length=50)
    description = models.TextField(_('Description'), null=True, blank=True)

    __unicode__ = lambda self: u'%s = %s' % (self.key, self.value)

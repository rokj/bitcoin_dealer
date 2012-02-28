from django.db import models

class UserSettings(SkeletonU):
    user = models.ForeignKey(User)
    key = models.CharField(_('Key'), max_length=50, null=False, blank=False, db_index=True)
    value = models.CharField(_('Value'), max_length=50)

    __unicode__ = lambda self: u'%s = %s' % (self.key, self.value)

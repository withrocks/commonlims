from __future__ import absolute_import


from django.db import models
from sentry.db.models import (Model, sane_repr)


class PluginRegistration(Model):
    """
    Lists every registration of a plugin, ensuring that configuration created by
    a plugin can be traced to a particular version of that plugin.
    """

    __core__ = True

    name = models.TextField(null=False)
    version = models.TextField(null=False)

    organization = models.ForeignKey('sentry.Organization')

    class Meta:
        app_label = 'clims'
        db_table = 'clims_pluginregistration'

    __repr__ = sane_repr('name', 'version')
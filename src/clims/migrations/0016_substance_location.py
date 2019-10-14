# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-10-13 13:23
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import sentry.db.models.fields.foreignkey


class Migration(migrations.Migration):

    dependencies = [
        ('clims', '0015_auto_20191004_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='substance',
            name='location',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clims.Location'),
        ),
    ]

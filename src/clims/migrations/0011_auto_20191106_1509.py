# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-11-06 15:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clims', '0010_searchindex'),
    ]

    operations = [
        migrations.RenameField(
            model_name='containerversion',
            old_name='previous_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='projectversion',
            old_name='previous_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='substanceversion',
            old_name='previous_name',
            new_name='name',
        ),
    ]

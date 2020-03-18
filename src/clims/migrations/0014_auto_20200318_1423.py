# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-03-18 14:23
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import sentry.db.models.fields.foreignkey


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clims', '0013_remove_pluginregistration_organization'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubstanceAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preset', models.TextField()),
                ('variables', jsonfield.fields.JSONField(default=dict)),
                ('status', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'clims_substanceassignment',
            },
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.TextField()),
                ('name', models.TextField()),
                ('version', models.IntegerField()),
                ('latest', models.BooleanField()),
                ('backend', models.TextField()),
            ],
            options={
                'db_table': 'clims_workflow',
            },
        ),
        migrations.RemoveField(
            model_name='workbatch',
            name='created',
        ),
        migrations.RemoveField(
            model_name='workbatch',
            name='plugin',
        ),
        migrations.AddField(
            model_name='pluginregistration',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pluginregistration',
            name='latest',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='substance',
            name='work_batches',
            field=models.ManyToManyField(related_name='substances', to='clims.WorkBatch'),
        ),
        migrations.AddField(
            model_name='workbatch',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2020, 3, 18, 14, 23, 20, 118894)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workbatch',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2020, 3, 18, 14, 23, 27, 892401)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workflow',
            name='plugin_registration',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clims.PluginRegistration'),
        ),
        migrations.AddField(
            model_name='substanceassignment',
            name='substance',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='clims.Substance'),
        ),
        migrations.AddField(
            model_name='substanceassignment',
            name='user',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='substanceassignment',
            name='workflow',
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clims.Workflow'),
        ),
    ]

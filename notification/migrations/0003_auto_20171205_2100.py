# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-05 13:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20171129_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
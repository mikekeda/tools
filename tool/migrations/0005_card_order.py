# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-01 07:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0004_auto_20170414_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
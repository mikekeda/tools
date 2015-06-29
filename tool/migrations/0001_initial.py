# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SimplePage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=60)),
                ('body', models.TextField(null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('changed_date', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(blank=True)),
            ],
        ),
    ]

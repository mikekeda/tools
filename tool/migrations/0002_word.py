# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-11 17:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('en', models.CharField(max_length=60, null=True)),
                ('es', models.CharField(max_length=60, null=True)),
                ('uk', models.CharField(max_length=60, null=True)),
                ('ru', models.CharField(max_length=60, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='words', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

# Generated by Django 2.0.2 on 2018-03-05 06:53

from django.db import migrations
import tool.models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0032_auto_20180304_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='color',
            field=tool.models.ColorField(default='000000', max_length=6),
        ),
    ]

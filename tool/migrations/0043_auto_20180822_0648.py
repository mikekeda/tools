# Generated by Django 2.1 on 2018-08-22 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0042_auto_20180822_0635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='timezone',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]

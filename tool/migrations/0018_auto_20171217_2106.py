# Generated by Django 2.0 on 2017-12-17 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0017_auto_20171217_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='password',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
# Generated by Django 2.1 on 2018-08-31 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0043_auto_20180822_0648'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='email',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='email_password',
        ),
    ]

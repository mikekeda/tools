# Generated by Django 2.0 on 2017-12-17 21:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0018_auto_20171217_2106'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='password',
            new_name='email_password',
        ),
    ]

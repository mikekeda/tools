# Generated by Django 2.0 on 2017-12-27 06:28

from django.db import migrations

from schedule.models import Rule


class Migration(migrations.Migration):
    def add_event_rules(apps, schema_editor):
        rules = [
            {
                'name': 'Daily',
                'description': 'Daily rule',
                'frequency': 'DAILY'
            },
            {
                'name': 'Weekly',
                'description': 'Weekly rule',
                'frequency': 'WEEKLY'
            },
            {
                'name': 'Monthly',
                'description': 'Monthly rule',
                'frequency': 'MONTHLY'
            },
            {
                'name': 'Yearly',
                'description': 'Yearly rule',
                'frequency': 'YEARLY'
            },
        ]
        for rule_data in rules:
            rule = Rule(**rule_data)
            rule.save()

    dependencies = [
        ('tool', '0025_auto_20171224_1818'),
    ]

    operations = [
        migrations.RunPython(add_event_rules),
    ]

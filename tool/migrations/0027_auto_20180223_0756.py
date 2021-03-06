# Generated by Django 2.0.2 on 2018-02-23 07:56

from schedule.models import Rule

from django.db import migrations


class Migration(migrations.Migration):
    def add_event_rules(apps, schema_editor):
        rules = [
            {
                'name': 'Work days',
                'description': 'workdays rule',
                'frequency': 'DAILY',
                'params': 'byweekday:0,1,2,3,4',
            },
            {
                'name': 'Any another day',
                'description': 'any another day rule',
                'frequency': 'DAILY',
                'params': 'interval:2',
            }
        ]
        for rule_data in rules:
            rule = Rule(**rule_data)
            rule.save()

    dependencies = [
        ('tool', '0026_auto_20171227_0628'),
    ]

    operations = [
        migrations.RunPython(add_event_rules),
    ]

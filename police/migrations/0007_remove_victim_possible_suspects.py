# Generated by Django 3.1.4 on 2021-01-09 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('police', '0006_auto_20210109_0841'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='victim',
            name='possible_suspects',
        ),
    ]

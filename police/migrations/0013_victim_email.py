# Generated by Django 3.1.4 on 2021-01-10 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('police', '0012_auto_20210110_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='victim',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
    ]

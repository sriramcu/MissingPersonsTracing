# Generated by Django 3.1.4 on 2021-01-09 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('police', '0009_auto_20210109_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='victim',
            name='dob',
            field=models.DateField(),
        ),
    ]

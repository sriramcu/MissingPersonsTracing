# Generated by Django 3.1.4 on 2021-01-15 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('police', '0014_input_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='input_image',
            name='placeholder',
            field=models.CharField(blank='', default='', max_length=40),
        ),
    ]

# Generated by Django 3.1.1 on 2020-09-13 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20200913_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardsetting',
            name='store_currency',
            field=models.CharField(choices=[('eur', 'Eur'), ('dollars', 'Dollars')], default='eur', max_length=10),
        ),
    ]

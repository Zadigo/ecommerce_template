# Generated by Django 3.1.1 on 2020-09-14 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_auto_20200913_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardsetting',
            name='store_currency',
            field=models.CharField(choices=[('eur', 'Eur'), ('dollars', 'Dollars')], default='eur', max_length=10),
        ),
    ]

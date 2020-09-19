# Generated by Django 3.1.1 on 2020-09-18 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_auto_20200918_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentoption',
            name='store_currency',
            field=models.CharField(choices=[('eur', 'Eur'), ('dollars', 'Dollars')], default='eur', max_length=10),
        ),
        migrations.AlterField(
            model_name='store',
            name='store_industry',
            field=models.CharField(choices=[('Fashion', 'Fashion'), ('clothing', 'Clothing'), ('jewelry', 'Jewelry')], default='Fashion', max_length=50),
        ),
    ]

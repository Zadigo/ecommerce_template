# Generated by Django 3.1.4 on 2020-12-28 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
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

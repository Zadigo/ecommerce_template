# Generated by Django 3.1.1 on 2020-11-20 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20201120_1201'),
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='products',
            field=models.ManyToManyField(null=True, to='shop.Product'),
        ),
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

# Generated by Django 3.1.1 on 2020-09-14 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_auto_20200914_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerorder',
            name='delivery',
            field=models.CharField(choices=[('standard', 'Standard')], default='standard', max_length=50),
        ),
        migrations.AlterField(
            model_name='customerorder',
            name='transaction',
            field=models.CharField(default='a9d6-911cac229bca39e61862e83a0298049433b81a205c92771b37fbfcddf24d0a07', max_length=200),
        ),
    ]
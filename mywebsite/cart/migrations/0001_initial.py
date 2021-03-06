# Generated by Django 3.1.1 on 2020-11-27 10:02

import cart.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.CharField(max_length=80)),
                ('price_pre_tax', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Price excluding taxes')),
                ('price_post_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Price including taxes')),
                ('color', models.CharField(max_length=50)),
                ('size', models.CharField(blank=True, max_length=5, null=True, validators=[cart.validators.generic_size_validator])),
                ('quantity', models.IntegerField(default=1, validators=[cart.validators.quantity_validator])),
                ('anonymous', models.BooleanField(default=False)),
                ('paid_for', models.BooleanField(default=False)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
            ],
            options={
                'ordering': ['-created_on', '-pk'],
            },
            managers=[
                ('cart_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='CustomerOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=50)),
                ('transaction', models.CharField(default='870b-911cac229bca39e61862e83a0298049433b81a205c92771b37fbfcddf24d0a07', max_length=200)),
                ('payment', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('accepted', models.BooleanField(default=False)),
                ('shipped', models.BooleanField(default=False)),
                ('refund', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True, max_length=500, null=True)),
                ('delivery', models.CharField(choices=[('standard', 'Standard'), ('prime', 'Prime')], default='standard', max_length=50)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('cart', models.ManyToManyField(blank=True, to='cart.Cart')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_on', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_number', models.CharField(blank=True, max_length=100, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('customer_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.customerorder')),
            ],
        ),
        migrations.AddIndex(
            model_name='customerorder',
            index=models.Index(fields=['payment'], name='cart_custom_payment_831246_idx'),
        ),
        migrations.AddIndex(
            model_name='cart',
            index=models.Index(fields=['price_pre_tax', 'quantity'], name='cart_cart_price_p_adbea5_idx'),
        ),
    ]

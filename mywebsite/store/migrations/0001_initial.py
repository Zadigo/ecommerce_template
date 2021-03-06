# Generated by Django 3.1.1 on 2020-11-27 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('contact_email', models.EmailField(max_length=100)),
                ('customer_care_email', models.EmailField(max_length=100)),
                ('store_industry', models.CharField(choices=[('Fashion', 'Fashion'), ('clothing', 'Clothing'), ('jewelry', 'Jewelry')], default='Fashion', max_length=50)),
                ('legal_name', models.CharField(blank=True, max_length=50, null=True)),
                ('telephone', models.CharField(blank=True, max_length=10, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=5, null=True)),
                ('accounts_disabled', models.BooleanField(default=True, help_text='The user can purchase even if he has an account')),
                ('accounts_optional', models.BooleanField(default=True, help_text='The user can purchase either as a registered or anonymous user')),
                ('mobile_banner', models.BooleanField(default=False, help_text='Show the mobile top banner')),
                ('nav_banner', models.BooleanField(default=False, help_text='Show the banner just below the navigation bar')),
                ('automatic_archive', models.BooleanField(default=False, help_text='Archive an order automatically after it has been fulfilled and paid')),
                ('allow_coupons', models.BooleanField(default=False)),
                ('allow_accounts', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('on_hold', models.BooleanField(default=False, help_text='Can access the store but cannot perform any actions')),
                ('created_on', models.DateField(auto_now_add=True)),
                ('products', models.ManyToManyField(blank=True, to='shop.Product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=80, null=True)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('website', models.URLField(blank=True, max_length=100, null=True)),
                ('archive', models.BooleanField(default=False)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.store')),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='PaymentOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_currency', models.CharField(choices=[('eur', 'Eur'), ('dollars', 'Dollars')], default='eur', max_length=10)),
                ('tax_rate', models.IntegerField(default=20)),
                ('stripe_live_key', models.CharField(blank=True, max_length=100)),
                ('stripe_secret_key', models.CharField(blank=True, max_length=100)),
                ('amazon_pay_key', models.CharField(blank=True, max_length=100)),
                ('enable_amazon_pay', models.BooleanField(default=False)),
                ('enable_apple_pay', models.BooleanField(default=False)),
                ('enable_google_pay', models.BooleanField(default=False)),
                ('store', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.store')),
            ],
        ),
        migrations.CreateModel(
            name='Analytic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('google_analytics', models.CharField(blank=True, max_length=50, null=True)),
                ('google_tag_manager', models.CharField(blank=True, max_length=50, null=True)),
                ('google_optimize', models.CharField(blank=True, max_length=50, null=True)),
                ('google_ads', models.CharField(blank=True, max_length=50, null=True)),
                ('facebook_pixels', models.CharField(blank=True, max_length=50, null=True)),
                ('mailchimp', models.CharField(blank=True, max_length=50, null=True)),
                ('store', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.store')),
            ],
        ),
        migrations.AddIndex(
            model_name='store',
            index=models.Index(fields=['name'], name='store_store_name_63b397_idx'),
        ),
        migrations.AddIndex(
            model_name='analytic',
            index=models.Index(fields=['google_analytics'], name='store_analy_google__b7146f_idx'),
        ),
    ]

# Generated by Django 3.1.1 on 2020-09-24 12:08

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import shop.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomaticCollectionCriteria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(default='NAW2020924f4b04e28cf', max_length=50)),
                ('condition', models.CharField(choices=[('is equal to', 'Is Equal To'), ('is not equal to', 'Is Not Equal To'), ('is greater than', 'Is Great Than'), ('is less than', 'Is Less Than'), ('starts with', 'Starts With'), ('ends with', 'Ends With'), ('contains', 'Contains'), ('does not contain', 'Does Not Contain'), ('yes', 'Yes'), ('no', 'No')], default='is equal to', max_length=50)),
                ('value', models.CharField(max_length=50)),
                ('modified_on', models.DateField(auto_now=True)),
                ('created_on', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('gender', models.CharField(choices=[('femme', 'Femme'), ('homme', 'Homme')], default='femme', max_length=50)),
                ('view_name', models.CharField(max_length=50)),
                ('image', models.FileField(blank=True, null=True, upload_to='collections')),
                ('presentation_text', models.TextField(blank=True, max_length=300, null=True)),
                ('google_description', models.CharField(blank=True, max_length=160, null=True)),
                ('show_presentation', models.BooleanField(default=False)),
                ('automatic', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-pk'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('variant', models.CharField(default='Noir', max_length=30)),
                ('aws_key', models.CharField(blank=True, max_length=50, null=True, verbose_name='AWS folder key')),
                ('aws_slug_name', models.CharField(blank=True, help_text='File name on AWS', max_length=100, null=True)),
                ('aws_image', models.BooleanField(default=False)),
                ('main_image', models.BooleanField(default=False, help_text='Indicates if this is the main image for the product')),
                ('url', models.URLField(blank=True, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='LookBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
                ('create_on', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('reference', models.CharField(default='SG1686DBA22B37', max_length=30)),
                ('gender', models.CharField(choices=[('femme', 'Femme'), ('homme', 'Homme')], default='femme', max_length=50)),
                ('description', models.TextField(blank=True, max_length=280, null=True)),
                ('description_html', models.TextField(blank=True, max_length=800, null=True)),
                ('description_objects', models.TextField(blank=True, max_length=800, null=True)),
                ('price_pre_tax', models.DecimalField(decimal_places=2, max_digits=5)),
                ('discount_pct', models.IntegerField(blank=True, default=10)),
                ('discounted_price', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('price_valid_until', models.DateField(default=datetime.date(2020, 10, 24))),
                ('quantity', models.IntegerField(blank=True, default=0)),
                ('sku', models.CharField(blank=True, help_text='ex. BCLOGO-GRIS-SMA', max_length=50, null=True)),
                ('google_category', models.CharField(choices=[('5424', 'Skirts'), ('212', 'Tops'), ('207', 'Shorts'), ('2271', 'Dresses'), ('214', 'Bras'), ('178', 'Accessories'), ('7366', 'Flyingtoyaccessories')], default='212', max_length=5)),
                ('in_stock', models.BooleanField(default=True)),
                ('discounted', models.BooleanField(default=False)),
                ('our_favorite', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('private', models.BooleanField(default=False, help_text='Product is on accessible by sharing the direct link')),
                ('slug', models.SlugField()),
                ('to_be_published_on', models.DateField(blank=True, default=django.utils.timezone.now)),
                ('last_modified', models.DateField(auto_now=True)),
                ('created_on', models.DateField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_on', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=3, null=True, validators=[shop.validators.generic_size_validator])),
                ('verbose_name', models.CharField(blank=True, max_length=50, null=True)),
                ('in_stock', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddIndex(
            model_name='variant',
            index=models.Index(fields=['name'], name='shop_varian_name_256798_idx'),
        ),
        migrations.AddField(
            model_name='product',
            name='collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.collection'),
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(to='shop.Image'),
        ),
        migrations.AddField(
            model_name='product',
            name='variant',
            field=models.ManyToManyField(blank=True, to='shop.Variant'),
        ),
        migrations.AddField(
            model_name='lookbook',
            name='products',
            field=models.ManyToManyField(to='shop.Product'),
        ),
        migrations.AddField(
            model_name='like',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.product'),
        ),
        migrations.AddField(
            model_name='like',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='image',
            index=models.Index(fields=['url'], name='shop_image_url_972fe2_idx'),
        ),
        migrations.AddField(
            model_name='collection',
            name='criterion',
            field=models.ManyToManyField(blank=True, to='shop.AutomaticCollectionCriteria'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['reference', 'collection', 'name'], name='shop_produc_referen_cd33b7_idx'),
        ),
    ]

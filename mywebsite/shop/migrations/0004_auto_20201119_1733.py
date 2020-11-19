# Generated by Django 3.1.1 on 2020-11-19 16:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20201118_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='image_url',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Product image'),
        ),
        migrations.AlterField(
            model_name='automaticcollectioncriteria',
            name='condition',
            field=models.CharField(choices=[('is equal to', 'Is Equal To'), ('is not equal to', 'Is Not Equal To'), ('is greater than', 'Is Great Than'), ('is less than', 'Is Less Than'), ('starts with', 'Starts With'), ('ends with', 'Ends With'), ('contains', 'Contains'), ('does not contain', 'Does Not Contain'), ('yes', 'Yes'), ('no', 'No')], default='is equal to', max_length=50),
        ),
        migrations.AlterField(
            model_name='automaticcollectioncriteria',
            name='reference',
            field=models.CharField(default='NAW2020111917221695cb', max_length=50),
        ),
        migrations.AlterField(
            model_name='collection',
            name='gender',
            field=models.CharField(choices=[('femme', 'Femme'), ('homme', 'Homme')], default='femme', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='gender',
            field=models.CharField(choices=[('femme', 'Femme'), ('homme', 'Homme')], default='femme', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='google_category',
            field=models.CharField(choices=[('5424', 'Skirts'), ('212', 'Tops'), ('207', 'Shorts'), ('2271', 'Dresses'), ('214', 'Bras'), ('178', 'Accessories'), ('7366', 'Flyingtoyaccessories')], default='212', max_length=5),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_valid_until',
            field=models.DateField(default=datetime.date(2020, 12, 19)),
        ),
        migrations.AlterField(
            model_name='product',
            name='reference',
            field=models.CharField(default='HT240026CA2C59', max_length=30),
        ),
    ]

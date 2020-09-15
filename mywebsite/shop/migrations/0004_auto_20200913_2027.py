# Generated by Django 3.1.1 on 2020-09-13 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20200913_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='automaticcollectioncriteria',
            name='condition',
            field=models.CharField(choices=[('is equal to', 'Is Equal To'), ('is not equal to', 'Is Not Equal To'), ('is greater than', 'Is Great Than'), ('is less than', 'Is Less Than'), ('starts with', 'Starts With'), ('ends with', 'Ends With'), ('contains', 'Contains'), ('does not contain', 'Does Not Contain'), ('yes', 'Yes'), ('no', 'No')], default='is equal to', max_length=50),
        ),
        migrations.AlterField(
            model_name='automaticcollectioncriteria',
            name='reference',
            field=models.CharField(default='NAW2020913849d436db1', max_length=50),
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
            name='reference',
            field=models.CharField(default='JG1006C7CAA336', max_length=30),
        ),
    ]

# Generated by Django 3.1.1 on 2020-09-15 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20200914_2252'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SubscribedUser',
        ),
    ]
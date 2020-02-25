# Generated by Django 3.0.3 on 2020-02-25 17:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20200225_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipapplication',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, help_text='Automatically set to now when membership application is created', verbose_name='Application creation date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='membershipapplication',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, help_text='Last time this membership application was modified', verbose_name='Last modified datetime'),
        ),
    ]

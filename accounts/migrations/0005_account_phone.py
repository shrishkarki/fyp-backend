# Generated by Django 4.0.4 on 2022-06-08 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_rename_opt_account_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='phone',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
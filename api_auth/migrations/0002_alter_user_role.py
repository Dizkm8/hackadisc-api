# Generated by Django 5.0.6 on 2024-06-21 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.IntegerField(choices=[(1, 'Admin Pignus'), (2, 'Admin Company'), (3, 'Admin Area'), (4, 'Admin Multicompany')], default=3),
        ),
    ]
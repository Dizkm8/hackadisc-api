# Generated by Django 5.0.6 on 2024-06-20 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_system', '0003_alter_company_main_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='state',
            field=models.IntegerField(choices=[(0, 'Not Evaluated'), (1, 'Evaluated'), (2, 'In Intervention'), (3, 'Intervened')], default=1),
        ),
    ]

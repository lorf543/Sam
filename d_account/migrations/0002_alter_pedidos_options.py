# Generated by Django 5.1.4 on 2025-01-29 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('d_account', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pedidos',
            options={'ordering': ['date_request'], 'verbose_name': 'Pedidos', 'verbose_name_plural': 'Pedidos'},
        ),
    ]

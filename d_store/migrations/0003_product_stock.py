# Generated by Django 5.1.4 on 2024-12-30 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('d_store', '0002_rename_part_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

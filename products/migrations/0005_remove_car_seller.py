# Generated by Django 4.2 on 2024-09-05 05:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_car_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='car',
            name='seller',
        ),
    ]

# Generated by Django 4.2 on 2024-09-08 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0007_alter_car_time'),
        ('ads', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ad',
            options={'ordering': ['-start_date'], 'verbose_name': 'Advertisement', 'verbose_name_plural': 'Advertisements'},
        ),
        migrations.RemoveField(
            model_name='ad',
            name='payment_status',
        ),
        migrations.AddField(
            model_name='ad',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('purchased', 'Purchased'), ('active', 'Active'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='ad',
            name='car',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ad', to='products.car'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ads', to=settings.AUTH_USER_MODEL),
        ),
    ]

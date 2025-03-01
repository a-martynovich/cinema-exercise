# Generated by Django 3.0.5 on 2020-05-19 07:11

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('booking_system', '0003_auto_20200519_0659'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='seat',
            managers=[
                ('manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='seat',
            name='booking',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='booking_system.Booking'),
        ),
    ]

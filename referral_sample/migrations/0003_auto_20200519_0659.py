# Generated by Django 3.0.5 on 2020-05-19 06:59

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('referral_sample', '0002_auto_20200519_0437'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='seat',
            managers=[
                ('booking_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='seat',
            name='state',
        ),
        migrations.RemoveField(
            model_name='seat',
            name='taken',
        ),
        migrations.AddField(
            model_name='booking',
            name='session_key',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='seat',
            name='booking',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='referral_sample.Booking'),
        ),
    ]

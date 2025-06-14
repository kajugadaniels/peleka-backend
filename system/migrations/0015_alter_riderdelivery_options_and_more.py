# Generated by Django 5.0.4 on 2024-11-11 11:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0014_alter_riderdelivery_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='riderdelivery',
            options={'verbose_name': 'Rider Delivery', 'verbose_name_plural': 'Rider Deliveries'},
        ),
        migrations.AlterField(
            model_name='riderdelivery',
            name='assigned_at',
            field=models.DateTimeField(blank=True, help_text='The timestamp when the rider was assigned to a delivery', null=True),
        ),
        migrations.AlterField(
            model_name='riderdelivery',
            name='current_status',
            field=models.CharField(choices=[('Available', 'Available'), ('Assigned', 'Assigned'), ('In Progress', 'In Progress'), ('Unavailable', 'Unavailable')], default='Available', help_text='Current status of the rider', max_length=20),
        ),
        migrations.AlterField(
            model_name='riderdelivery',
            name='delivered_at',
            field=models.DateTimeField(blank=True, help_text='The timestamp when the delivery was completed', null=True),
        ),
        migrations.AlterField(
            model_name='riderdelivery',
            name='delivery_request',
            field=models.ForeignKey(blank=True, help_text='The delivery request currently assigned to the rider', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rider_assignment', to='system.deliveryrequest'),
        ),
        migrations.AlterField(
            model_name='riderdelivery',
            name='in_progress_at',
            field=models.DateTimeField(blank=True, help_text='The timestamp when the delivery started', null=True),
        ),
        migrations.AlterField(
            model_name='riderdelivery',
            name='last_assigned_at',
            field=models.DateTimeField(blank=True, help_text='The last time the rider was assigned a delivery', null=True),
        ),
        migrations.AlterField(
            model_name='riderdelivery',
            name='rider',
            field=models.ForeignKey(help_text='The rider assigned to deliveries', on_delete=django.db.models.deletion.CASCADE, related_name='rider_delivery', to='system.rider'),
        ),
    ]

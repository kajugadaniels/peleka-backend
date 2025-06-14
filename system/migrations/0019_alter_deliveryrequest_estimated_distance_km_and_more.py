# Generated by Django 5.0 on 2025-01-04 15:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0018_alter_rider_permit_image'),
        ('web', '0002_rename_contactus_contact_alter_contact_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryrequest',
            name='estimated_distance_km',
            field=models.CharField(blank=True, help_text='Estimated distance of the delivery in kilometers', max_length=15, null=True),
        ),
        migrations.CreateModel(
            name='BookRiderAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(blank=True, help_text='Timestamp when the rider was assigned', null=True)),
                ('in_progress_at', models.DateTimeField(blank=True, help_text='Timestamp when the booking started', null=True)),
                ('completed_at', models.DateTimeField(blank=True, help_text='Timestamp when the booking was completed', null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, help_text='Timestamp when the booking was cancelled', null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('In Progress', 'In Progress'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', help_text='Current status of the assignment', max_length=20)),
                ('book_rider', models.ForeignKey(help_text='The booking request to which the rider is assigned', on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='web.bookrider')),
                ('rider', models.ForeignKey(help_text='The rider assigned to the booking', on_delete=django.db.models.deletion.CASCADE, related_name='book_rider_assignments', to='system.rider')),
            ],
            options={
                'verbose_name': 'Book Rider Assignment',
                'verbose_name_plural': 'Book Rider Assignments',
                'ordering': ['-assigned_at'],
            },
        ),
    ]

# Generated by Django 5.1.3 on 2024-11-05 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task_data_app', '0008_task_priority'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='priority',
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-22 10:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_data_app', '0015_remove_task_subtask_task_subtask'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='subtask',
        ),
        migrations.AddField(
            model_name='subtask',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='task_data_app.task'),
        ),
    ]
# Generated by Django 5.1.3 on 2024-12-03 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_data_app', '0012_alter_task_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtask',
            name='name',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='task',
            name='priorityImg',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]

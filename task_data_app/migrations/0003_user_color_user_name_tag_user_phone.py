# Generated by Django 5.1.3 on 2024-11-05 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_data_app', '0002_alter_user_date_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='color',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AddField(
            model_name='user',
            name='name_tag',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
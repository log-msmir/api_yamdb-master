# Generated by Django 3.0.5 on 2023-01-13 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20230113_1357'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='description',
            new_name='bio',
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(default='user', max_length=50),
        ),
    ]
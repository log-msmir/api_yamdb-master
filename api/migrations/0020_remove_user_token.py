# Generated by Django 3.0.5 on 2023-02-02 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_remove_user_confirmation_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='token',
        ),
    ]
# Generated by Django 4.2.19 on 2025-02-27 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_allow_user_password2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='allow',
            field=models.BooleanField(default=True),
        ),
    ]

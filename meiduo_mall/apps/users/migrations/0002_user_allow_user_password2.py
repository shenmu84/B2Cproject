# Generated by Django 4.2.19 on 2025-02-27 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='allow',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='password2',
            field=models.CharField(default='1234567890', max_length=10),
        ),
    ]

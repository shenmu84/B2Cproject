# Generated by Django 4.2.19 on 2025-03-16 04:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_options_remove_user_allow_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='mail_active',
            new_name='email_active',
        ),
    ]

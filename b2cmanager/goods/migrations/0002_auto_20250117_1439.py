# Generated by Django 2.2.5 on 2025-01-17 06:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
                ('pub_date', models.DateField(null=True)),
                ('readcount', models.IntegerField(default=0)),
                ('commentcount', models.IntegerField(default=0)),
                ('is_delete', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '货物管理',
                'db_table': 'goodinfo',
            },
        ),
        migrations.RenameModel(
            old_name='Goods',
            new_name='Good',
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
                ('gendere', models.SmallIntegerField(choices=[(1, 'male'), (2, 'female')], default=1)),
                ('description', models.CharField(max_length=100, null=True)),
                ('is_delete', models.BooleanField(default=False)),
                ('good', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.GoodInfo')),
            ],
            options={
                'db_table': 'userinfo',
            },
        ),
    ]

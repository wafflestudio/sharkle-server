# Generated by Django 3.2.6 on 2022-03-17 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('last_update', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('code', models.PositiveIntegerField()),
            ],
        ),
    ]
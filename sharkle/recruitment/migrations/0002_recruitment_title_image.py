# Generated by Django 3.2.6 on 2022-09-14 18:56

from django.db import migrations, models
import sharkle.upload_image


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruitment',
            name='title_image',
            field=models.ImageField(null=True, upload_to=sharkle.upload_image.upload_image),
        ),
    ]

# Generated by Django 4.1.7 on 2023-05-23 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='static/img/base.jpeg', null=True, upload_to='static/img/', verbose_name='Аватарка'),
        ),
    ]

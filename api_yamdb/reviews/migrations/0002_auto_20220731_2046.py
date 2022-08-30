# Generated by Django 2.2.16 on 2022-07-31 17:46

import reviews.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[reviews.validators.username_validation], verbose_name='Ник пользователя'),
        ),
    ]

# Generated by Django 3.2.8 on 2022-03-10 06:47

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0010_album_song'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='uploaded_on',
            field=models.DateField(default=datetime.datetime(2022, 3, 10, 6, 47, 56, 901745, tzinfo=utc)),
        ),
    ]
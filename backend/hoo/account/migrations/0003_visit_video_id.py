# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 12:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20170503_2130'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='video_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

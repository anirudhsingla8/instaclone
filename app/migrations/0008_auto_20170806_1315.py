# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-06 07:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cloneapp', '0007_categorymodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categorymodel',
            name='post',
        ),
        migrations.DeleteModel(
            name='CategoryModel',
        ),
    ]
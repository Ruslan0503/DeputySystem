# Generated by Django 5.1.7 on 2025-04-24 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a1', '0009_organizesession_passed'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizesession',
            name='title',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.1.7 on 2025-04-03 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a1', '0002_alter_profile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.ManyToManyField(blank=True, related_name='RoleOfUser', to='a1.role'),
        ),
    ]

# Generated by Django 3.0.4 on 2020-03-11 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schoolapp', '0004_auto_20200311_0318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='selected_timestamp',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]

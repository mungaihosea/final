# Generated by Django 3.0.4 on 2020-03-12 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schoolapp', '0010_auto_20200311_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='adm_date',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='date_of_birth',
            field=models.TextField(blank=True, null=True),
        ),
    ]

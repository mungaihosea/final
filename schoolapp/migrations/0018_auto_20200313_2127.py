# Generated by Django 3.0.4 on 2020-03-13 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schoolapp', '0017_hod'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectgradingsystem',
            name='Fplain_lower',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='subjectgradingsystem',
            name='Fplain_points',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='subjectgradingsystem',
            name='Fplain_upper',
            field=models.IntegerField(null=True),
        ),
    ]

# Generated by Django 3.0.4 on 2020-03-13 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schoolapp', '0013_alumni'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='form1term1_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='form1term2_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='form1term3_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='form2term1_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='form2term2_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='form2term3_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='form3term1_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='form3term2_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='form3term3_closing_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

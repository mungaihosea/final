# Generated by Django 3.0.4 on 2020-03-13 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schoolapp', '0016_teacher_initials'),
    ]

    operations = [
        migrations.CreateModel(
            name='HOD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='schoolapp.Subject')),
                ('teacher', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='schoolapp.Teacher')),
            ],
        ),
    ]

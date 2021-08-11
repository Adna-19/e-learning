# Generated by Django 3.1.7 on 2021-03-14 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        ('accounts', '0002_auto_20210311_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructorprofile',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=10),
        ),
        migrations.AlterField(
            model_name='instructorprofile',
            name='major_subjects',
            field=models.ManyToManyField(blank=True, null=True, to='courses.Subject'),
        ),
    ]
# Generated by Django 3.2.4 on 2021-08-03 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0023_acheivement_date_created'),
        ('quiz', '0002_remove_quiz_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='module',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attached_quiz', to='courses.module'),
        ),
    ]

# Generated by Django 3.2.4 on 2021-08-01 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_user_profile_image'),
        ('courses', '0017_module_opened'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='opened',
        ),
        migrations.AddField(
            model_name='module',
            name='students_viewed',
            field=models.ManyToManyField(blank=True, null=True, to='accounts.StudentProfile'),
        ),
    ]

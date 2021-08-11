# Generated by Django 3.2.4 on 2021-06-27 14:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0002_comment_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commentreply',
            old_name='comment',
            new_name='reply_to',
        ),
        migrations.AddField(
            model_name='commentreply',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='commentreply',
            name='reply_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

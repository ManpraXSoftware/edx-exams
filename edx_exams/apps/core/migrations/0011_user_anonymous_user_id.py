# Generated by Django 3.2.15 on 2022-09-28 18:35

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_user_anonymous_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='anonymous_user_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
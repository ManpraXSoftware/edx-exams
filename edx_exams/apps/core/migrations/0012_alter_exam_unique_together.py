# Generated by Django 3.2.16 on 2022-11-10 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_user_anonymous_user_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='exam',
            unique_together=set(),
        ),
    ]

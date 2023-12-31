# Generated by Django 4.1.2 on 2023-02-05 10:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0020_alter_answer_options_alter_comment_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='learned_by_users',
            field=models.ManyToManyField(related_name='learned_by_users', to=settings.AUTH_USER_MODEL, verbose_name='Изучено пользователями'),
        ),
    ]

# Generated by Django 4.1.2 on 2022-12-10 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_topic_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='text',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
    ]

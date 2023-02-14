# Generated by Django 2.2.9 on 2023-02-14 20:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={
                'ordering': ('-pub_date',),
                'verbose_name': 'комментарий',
                'verbose_name_plural': 'комментарии',
            },
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={
                'verbose_name': 'подписчик',
                'verbose_name_plural': 'подписчики',
            },
        ),
        migrations.RemoveField(
            model_name='post',
            name='created',
        ),
        migrations.AddField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='дата публикации',
            ),
            preserve_default=False,
        ),
    ]

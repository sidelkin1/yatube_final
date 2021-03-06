# Generated by Django 3.2.1 on 2022-06-09 13:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0002_post_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='rating',
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(blank=True, choices=[(None, '-пусто-'), (1, '★☆☆☆☆'), (2, '★★☆☆☆'), (3, '★★★☆☆'), (4, '★★★★☆'), (5, '★★★★★')], help_text='Введите рейтинг поста', null=True, verbose_name='Рейтинг')),
                ('post', models.ForeignKey(help_text='Введите номер поста', on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='posts.post', verbose_name='Пост')),
                ('user', models.ForeignKey(help_text='Введите имя пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Рейтинг',
                'verbose_name_plural': 'Рейтинги',
            },
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(fields=('user', 'post'), name='unique_user_post'),
        ),
    ]

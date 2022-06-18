from django.contrib.auth import get_user_model
from django.db import models

# Модель данных пользователя поста
User = get_user_model()

# Рейтинг поста
RATING_CHOICES = (
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
)


class Group(models.Model):
    """Модель группы постов."""

    # Название группы
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Введите название группы'
    )
    # URL группы
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL группы',
        help_text='Введите URL группы'
    )
    # Детальное описание группы
    description = models.TextField(verbose_name='Описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['title']

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """Модель поста."""

    # Текст поста
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    # Дата поста
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Введите дату публикации'
    )
    # Связь с автором поста
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Пользователь',
        help_text='Введите имя пользователя'
    )
    # Связь с группой постов
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True, null=True,
        verbose_name='Группа',
        help_text='Введите название группы'
    )
    # Поле для картинки (необязательное)
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка',
        help_text='Добавьте картинку'
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:15]

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)


class Comment(models.Model):
    """Модель комментария."""

    # Связь с постом
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Введите номер поста'
    )
    # Связь с автором поста
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пользователь',
        help_text='Введите имя пользователя'
    )
    # Текст комментария
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    # Дата комментария
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
        help_text='Введите дату комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created']


class Follow(models.Model):
    """Модель подписки."""

    # Пользователь, который подписывается
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Введите подписчика'
    )
    # Пользователь, на которого подписываются
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Введите автора'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow',
            ),
        ]


class Rating(models.Model):
    """Модель рейтинга поста."""

    # Пользователь, который поставил рейтинг
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Пользователь',
        help_text='Введите имя пользователя'
    )
    # Связь с постом
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Пост',
        help_text='Введите номер поста'
    )
    # Рейтинг поста
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        verbose_name='Рейтинг',
        help_text='Введите рейтинг поста'
    )

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_user_post'
            ),
        ]

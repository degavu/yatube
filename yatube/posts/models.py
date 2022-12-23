from django.db import models
from django.contrib.auth import get_user_model

from .validators import min_size, size_comment


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Группа',
        help_text='Название группы, не больше 200 символов'
    )
    slug = models.SlugField(
        unique=True,
        editable=True,
        verbose_name='Уникальное имя группы',
        help_text='Можно использовать только латинские буквы и цифры'
    )
    description = models.TextField(
        default='Полное описание сообщества',
        verbose_name='Описание сообщества',
    )

    def __str__(self) -> str:
        return str(self.title)


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        validators=[min_size],
        help_text='Введите текст поста, не меньше 10 символов'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Заполняется автоматически'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий к посту',
        help_text='Для какого поста этот комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Кто автор этого комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        max_length=140,
        help_text='Введите текст от 3-х до 140 символов',
        blank=False,
        validators=[size_comment],
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время комментария',
        help_text='Завполняется автоматически'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f'{self.author}: {self.text[:15]}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на кого подписан'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique subscription'
                                    )
        ]

    def __str__(self) -> str:
        return f'{self.user} to: {self.author}'

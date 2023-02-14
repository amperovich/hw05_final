from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PublicateModel(models.Model):
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Group(models.Model):
    namemaxlength = 200
    title = models.CharField(
        max_length=namemaxlength,
        verbose_name='название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='ссылка',
    )
    description = models.TextField(verbose_name='описание')

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self) -> str:
        return self.title


class Post(PublicateModel):
    text = models.TextField(verbose_name='текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор поста',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='группа, опубликовавшая пост',
    )
    image = models.ImageField(
        blank=True,
        upload_to='posts/',
        verbose_name='картинка',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return self.text[:settings.POST_CHARS]  # fmt: skip


class Comment(PublicateModel):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='пост, к которому относится комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
    )
    text = models.TextField(
        verbose_name='текст комментария',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
    )

    constraints = [
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_users',
        ),
    ]

    class Meta:
        verbose_name = 'подписчик'
        verbose_name_plural = 'подписчики'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
